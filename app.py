import random
import time
import streamlit as st

st.set_page_config(page_title="Slot Machine", page_icon="🎰", layout="centered")

SYMBOLS = ['🍒', '🍉', '🍋', '⭐', '🔔']

# Inisialisasi saldo di memori sesi browser (tanpa akun/database)
if 'balance' not in st.session_state:
    st.session_state.balance = 100
if 'last_row' not in st.session_state:
    st.session_state.last_row = ['🍒', '🍉', '🍋']
if 'message' not in st.session_state:
    st.session_state.message = ("info", "Masukkan jumlah taruhan dan klik **Spin!** untuk mulai bermain.")

def spin_row():
    return [random.choice(SYMBOLS) for _ in range(3)]

def get_payout(row, bet):
    if row[0] == row[1] == row[2]:
        multipliers = {
            '🍒': 5,
            '🍉': 10,
            '🍋': 15,
            '⭐': 20,
            '🔔': 30
        }
        return bet * multipliers.get(row[0], 0)
    return 0

def render_slot_box(symbols_list, status_text=""):
    display_str = " &nbsp;|&nbsp; ".join(symbols_list)
    return f"""
    <div style="
        background-color: #1e1e2e;
        border: 3px solid #f59e0b;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        margin: 15px 0;
    ">
        <div style="font-size: 14px; color: #9ca3af; margin-bottom: 10px;">{status_text}</div>
        <div style="font-size: 54px; letter-spacing: 8px;">{display_str}</div>
    </div>
    """

# --- TAMPILAN UTAMA ---
st.title("🎰 Slot Machine")
st.caption("Simbol & Hadiah: 🍒 (5x) | 🍉 (10x) | 🍋 (15x) | ⭐ (20x) | 🔔 (30x)")

# Menampilkan saldo saat ini
st.metric(label="Current Balance", value=f"${st.session_state.balance:,.2f}")

# Area kotak mesin slot (bisa diperbarui secara real-time saat animasi)
slot_placeholder = st.empty()
slot_placeholder.markdown(
    render_slot_box(st.session_state.last_row, "READY"),
    unsafe_allow_html=True
)

# Jika saldo habis
if st.session_state.balance <= 0:
    st.error("No money to bet on, Play again?")
    if st.button("🔄 Main Lagi (Reset Saldo $100)", use_container_width=True):
        st.session_state.balance = 100
        st.session_state.last_row = ['🍒', '🍉', '🍋']
        st.session_state.message = ("info", "Saldo telah di-reset ke $100!")
        st.rerun()
else:
    # Form input taruhan
    col1, col2 = st.columns([2, 1])
    with col1:
        bet = st.number_input(
            "Input the Bet ($):",
            min_value=0.01,
            max_value=float(st.session_state.balance),
            value=min(10, float(st.session_state.balance)),
            step=1
        )
    with col2:
        st.write("")
        st.write("")
        spin_clicked = st.button("🎲 SPIN!", type="primary", use_container_width=True)

    if spin_clicked:
        if bet > st.session_state.balance:
            st.warning("Balance not enough...")
        elif bet <= 0:
            st.warning("Can't do that...")
        else:
            # Kurangi saldo & tentukan hasil akhir
            st.session_state.balance -= bet
            final_row = spin_row()

            # Animasi putaran reel persis seperti efek perlambatan kubik di kode asli Anda
            locked_symbols = []
            for target_symbol in final_row:
                target_idx = SYMBOLS.index(target_symbol)
                total_steps = 14

                for step in range(total_steps):
                    current_idx = (target_idx - (total_steps - step)) % len(SYMBOLS)
                    temp_symbol = SYMBOLS[current_idx]
                    remaining_slots = ['❓'] * (2 - len(locked_symbols))
                    current_view = locked_symbols + [temp_symbol] + remaining_slots

                    slot_placeholder.markdown(
                        render_slot_box(current_view, "SPINNING..."),
                        unsafe_allow_html=True
                    )

                    progress = step / total_steps
                    delay = 0.02 + (progress ** 3) * 0.20
                    time.sleep(delay)

                locked_symbols.append(target_symbol)
                remaining_slots = ['❓'] * (3 - len(locked_symbols))
                slot_placeholder.markdown(
                    render_slot_box(locked_symbols + remaining_slots, "SPINNING..."),
                    unsafe_allow_html=True
                )
                time.sleep(0.12)

            # Simpan hasil & hitung hadiah
            st.session_state.last_row = final_row
            payout = get_payout(final_row, bet)

            if payout > 0:
                st.session_state.balance += payout
                st.session_state.message = ("success", f"🎉 You won **${payout}**!")
            else:
                st.session_state.message = ("error", "Sorry you lost this round.")

            st.rerun()

# Tampilkan pesan status putaran terakhir
msg_type, msg_text = st.session_state.message
if msg_type == "success":
    st.success(msg_text)
    st.balloons()
elif msg_type == "error":
    st.error(msg_text)
else:
    st.info(msg_text)
