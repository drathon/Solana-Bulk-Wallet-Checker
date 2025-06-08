import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.keypair import Keypair
import base58
import threading
import time
import os
import queue

class SolanaChecker(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dr. Athon Solana Wallet Checker")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Dr. Athon Solana Wallet Checker",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(pady=20)

        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20)

        self.convert_button = ctk.CTkButton(
            self.button_frame,
            text="Convert Private Keys",
            command=self.convert_private_keys,
            width=200
        )
        self.convert_button.pack(pady=10)

        self.check_balance_button = ctk.CTkButton(
            self.button_frame,
            text="Check Balances",
            command=self.check_balances,
            width=200
        )
        self.check_balance_button.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Helvetica", 12)
        )
        self.progress_label.pack(pady=5)

        self.result_text = ctk.CTkTextbox(
            self.main_frame,
            width=700,
            height=300
        )
        self.result_text.pack(pady=20)

        self.client = Client("https://api.mainnet-beta.solana.com")
        self.queue = queue.Queue()

    def update_ui(self):
        try:
            while True:
                message = self.queue.get_nowait()
                if message.startswith("PROGRESS:"):
                    progress = float(message.split(":")[1])
                    self.progress_bar.set(progress)
                    self.progress_label.configure(text=f"%{int(progress * 100)}")
                elif message.startswith("RESULT:"):
                    self.result_text.insert(tk.END, message[7:] + "\n")
                    self.result_text.see(tk.END)
                elif message == "DONE":
                    self.convert_button.configure(state="normal")
                    self.check_balance_button.configure(state="normal")
                    return
        except queue.Empty:
            pass
        finally:
            self.after(100, self.update_ui)

    def convert_private_keys(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        try:
            self.convert_button.configure(state="disabled")
            self.check_balance_button.configure(state="disabled")

            with open(file_path, 'r') as file:
                private_keys = [line.strip() for line in file if line.strip()]

            self.result_text.delete("1.0", tk.END)
            self.queue.put("RESULT:Starting conversion...\n\n")

            results = []

            def process_keys():
                total_keys = len(private_keys)
                for i, private_key in enumerate(private_keys, 1):
                    try:
                        secret = base58.b58decode(private_key)
                        if len(secret) != 64:
                            self.queue.put(f"RESULT:⛔ Invalid length: {private_key[:8]}...\n\n")
                            continue

                        kp = Keypair.from_bytes(secret)
                        pubkey = kp.pubkey()
                        
                        results.append(f"wallet: {pubkey}\n")
                        results.append(f"private: {private_key}\n\n")
                        
                        self.queue.put(f"RESULT:✅ {i}. Private Key: {private_key[:8]}...\n   Public Key: {pubkey}\n\n")
                        self.queue.put(f"PROGRESS:{i / total_keys}")

                    except Exception as e:
                        self.queue.put(f"RESULT:❌ Error: {str(e)}\n\n")

                with open("wallets.txt", "w") as out:
                    out.writelines(results)

                self.queue.put("RESULT:Conversion complete!\n")
                self.queue.put("DONE")

            thread = threading.Thread(target=process_keys)
            thread.start()
            self.update_ui()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.convert_button.configure(state="normal")
            self.check_balance_button.configure(state="normal")

    def check_balances(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        try:
            self.convert_button.configure(state="disabled")
            self.check_balance_button.configure(state="disabled")

            wallets = []
            with open(file_path, "r") as f:
                for line in f:
                    if line.lower().startswith("wallet:"):
                        wallet_address = line.strip().split("wallet:")[1].strip()
                        if wallet_address:
                            wallets.append(wallet_address)

            self.result_text.delete("1.0", tk.END)
            self.queue.put("RESULT:Checking balances...\n\n")

            results = []

            def check_balances_thread():
                total_wallets = len(wallets)
                for i, wallet in enumerate(wallets, 1):
                    try:
                        pubkey = Pubkey.from_string(wallet)
                        sol = self.client.get_balance(pubkey).value / 1_000_000_000
                        
                        self.queue.put(f"RESULT:🔑 Wallet: {wallet}\n💰 SOL: {sol:.5f} SOL\n\n")

                        if sol > 0:
                            results.append(f"wallet: {wallet}\n")
                            results.append(f"balance: {sol:.5f} SOL\n\n")

                        self.queue.put(f"PROGRESS:{i / total_wallets}")

                    except Exception as e:
                        self.queue.put(f"RESULT:❌ Error: {wallet[:8]}...: {str(e)}\n\n")

                    if i % 15 == 0:
                        self.queue.put("RESULT:⏳ 15 queries done, waiting 5 sec...\n\n")
                        time.sleep(5)
                    else:
                        time.sleep(0.4)

                with open("active_wallets.txt", "w") as out_file:
                    out_file.writelines(results)

                self.queue.put("RESULT:Balance check complete!\n")
                self.queue.put("DONE")

            thread = threading.Thread(target=check_balances_thread)
            thread.start()
            self.update_ui()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.convert_button.configure(state="normal")
            self.check_balance_button.configure(state="normal")

if __name__ == "__main__":
    app = SolanaChecker()
    app.mainloop()
