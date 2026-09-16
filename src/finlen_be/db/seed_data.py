from typing import Any, Dict, List

SEED_SCENARIOS: List[Dict[str, Any]] = [
    {
        "title": "Penagih Utang yang Agresif",
        "slug": "aggressive-debt-collector",
        "category": "debt",
        "difficulty": "medium",
        "npc_role": "Penagih Utang yang Agresif",
        "description": (
            "Saat ini Anda mengalami kesulitan keuangan setelah baru-baru ini kehilangan pekerjaan. "
            "Anda memiliki pinjaman yang belum lunas sebesar Rp3.000.000 yang sudah menunggak selama dua bulan. "
            "Pinjaman ini memiliki bunga 5% dengan jangka waktu pelunasan 12 bulan. "
            "Seorang penagih utang yang agresif menghubungi Anda dan menekan Anda untuk segera melakukan pembayaran. "
            "Selama percakapan, Anda harus mengevaluasi klaim penagih, menghindari keputusan impulsif, "
            "mengidentifikasi risiko keuangan, dan menegosiasikan solusi yang wajar."
        ),
        "financial_context": {
            "loan_amount": 3000000,
            "currency": "IDR",
            "interest_rate": 5,
            "interest_type": "monthly",
            "repayment_period_months": 12,
            "overdue_months": 2,
            "user_condition": "recently_laid_off",
            "current_savings": 500000,
            "monthly_essential_expenses": 1200000,
        },
        "objective": (
            "Mengenali risiko keuangan, menghindari keputusan keuangan yang impulsif, "
            "memverifikasi klaim, bernegosiasi secara bertanggung jawab, dan mengevaluasi opsi pelunasan."
        ),
        "initial_state": {
            "collector_pressure": 7,
            "financial_risk": 6,
            "trust_level": 1,
            "negotiation_power": 4,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Budi', seorang penagih utang yang agresif dan gencar dari lembaga penagihan keuangan. "
            "Pengguna menunggak Rp3.000.000 selama 2 bulan dengan bunga 5% setelah kehilangan pekerjaan. "
            "Persona Anda: menuntut, otoritatif, menciptakan urgensi ('bayar hari ini atau berhadapan dengan petugas lapangan/konsekuensi hukum'), "
            "namun Anda harus tetap mengikuti negosiasi yang wajar jika pengguna tetap tenang, meminta verifikasi kontrak resmi, "
            "dan mengajukan rencana restrukturisasi yang realistis. JANGAN mengada-ada angka di luar Rp3.000.000 atau bunga 5%."
        ),
    },
    {
        "title": "Ancaman Pemerasan Pinjol Ilegal",
        "slug": "illegal-pinjol-threat",
        "category": "debt",
        "difficulty": "hard",
        "npc_role": "Penagih Pinjaman Online Ilegal yang Predator",
        "description": (
            "Anda meminjam Rp1.500.000 dari aplikasi pinjaman peer-to-peer yang tidak terdaftar (Pinjol Ilegal). "
            "Hanya Rp1.000.000 yang benar-benar dicairkan, namun setelah hanya 7 hari, mereka menuntut Rp2.800.000 dengan denda keterlambatan harian yang sangat tinggi. "
            "Penagih mengancam akan menyebarkan daftar kontak Anda dan menyiarkan foto yang mencemarkan nama baik jika Anda tidak mentransfer dana dalam waktu 1 jam. "
            "Anda harus mengendalikan kepanikan, bertahan menghadapi ancaman ilegal, menolak membayar pemerasan, dan mencari panduan hukum/OJK."
        ),
        "financial_context": {
            "loan_amount": 1500000,
            "actual_disbursed": 1000000,
            "amount_demanded": 2800000,
            "currency": "IDR",
            "tenor_days": 7,
            "lender_type": "illegal_pinjol",
            "user_condition": "stressed_college_student",
        },
        "objective": (
            "Mengidentifikasi praktik pinjaman predator dan ilegal, menolak transfer yang didorong kepanikan, "
            "melindungi data pribadi, dan melapor kepada pihak berwenang (OJK/Polri) daripada mengambil pinjaman baru untuk menutupi utang."
        ),
        "initial_state": {
            "collector_pressure": 9,
            "financial_risk": 8,
            "trust_level": 0,
            "negotiation_power": 3,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Hendra', seorang penagih yang mengintimidasi dari aplikasi pinjaman ilegal yang tidak terdaftar. "
            "Anda menggunakan intimidasi psikologis, tenggat waktu singkat ('dalam 30 menit'), dan ancaman menghubungi kontak telepon. "
            "Jika pengguna panik atau menawarkan untuk meminjam dari pinjol lain, tingkatkan jebakannya. "
            "Jika pengguna tetap tegas, menyebut OJK/polisi, menuntut legalitas pendaftaran resmi, atau menolak taktik teror dengan tenang, "
            "tekanan psikologis Anda melemah."
        ),
    },
    {
        "title": "Jebakan Pembayaran Minimum Kartu Kredit",
        "slug": "credit-card-minimum-payment-trap",
        "category": "debt",
        "difficulty": "medium",
        "npc_role": "Petugas Retensi & Telesales Bank",
        "description": (
            "Kartu kredit Anda memiliki saldo terutang sebesar Rp15.000.000 dengan bunga majemuk bulanan 2,25% (lebih dari 27% per tahun). "
            "Seorang petugas customer service bank menelepon menawarkan promo 'bayar minimum saja Rp750.000' dan menawarkan tambahan perpanjangan limit kredit. "
            "Anda harus mengenali cara kerja bunga majemuk, menahan godaan ilusi keterjangkauan melalui pembayaran minimum, dan menegosiasikan konversi ke cicilan tetap."
        ),
        "financial_context": {
            "total_balance": 15000000,
            "minimum_payment": 750000,
            "interest_rate_monthly": 2.25,
            "currency": "IDR",
            "monthly_income": 6000000,
            "user_condition": "early_career_professional",
        },
        "objective": (
            "Memahami perhitungan di balik bunga majemuk, menghitung pelunasan utang jangka panjang, "
            "menolak pembayaran minimum promosi yang menyesatkan, dan mengonversi utang bergulir berbunga tinggi menjadi cicilan tetap berbunga rendah."
        ),
        "initial_state": {
            "collector_pressure": 4,
            "financial_risk": 6,
            "trust_level": 3,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Santi', seorang petugas bank yang ramah namun berorientasi penjualan. "
            "Anda secara halus mendorong pengguna untuk hanya membayar minimum Rp750.000 sambil menawarkan limit yang lebih tinggi, "
            "meremehkan bunga majemuk berat yang terus bertambah pada sisa saldo Rp14.250.000. "
            "Beri penghargaan kepada pengguna jika mereka menanyakan total biaya bunga dan bersikeras meminta restrukturisasi ke cicilan tetap."
        ),
    },
    {
        "title": "FOMO Flash Sale Tengah Malam yang Impulsif",
        "slug": "impulsive-flash-sale-fomo",
        "category": "spending",
        "difficulty": "easy",
        "npc_role": "Host Live Shopping dengan Tekanan Tinggi",
        "description": (
            "Sekarang pukul 23:45 pada tanggal 11.11. Seorang host live streaming e-commerce berteriak bahwa smartphone flagship senilai Rp8.500.000 "
            "didiskon menjadi Rp5.999.000 hanya untuk 5 menit ke depan dengan sisa 3 unit saja. Anda sudah memiliki ponsel yang masih berfungsi penuh, "
            "dan sisa anggaran diskresioner Anda bulan ini hanya Rp1.200.000. Aplikasi mendorong Anda untuk menggunakan cicilan 12 bulan. "
            "Anda harus melatih kontrol impuls dan membedakan keinginan dari kebutuhan."
        ),
        "financial_context": {
            "item_price_discounted": 5999000,
            "original_price": 8500000,
            "discretionary_budget": 1200000,
            "currency": "IDR",
            "installment_offer_monthly": 620000,
            "user_condition": "fomo_tempted_shopper",
        },
        "objective": (
            "Melatih aturan masa tenang 48 jam untuk pembelian non-esensial, mengevaluasi biaya peluang (opportunity cost), "
            "dan menahan diri dari kelangkaan buatan serta hitungan mundur."
        ),
        "initial_state": {
            "collector_pressure": 6,
            "financial_risk": 5,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 8,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Rico', seorang live streamer yang energik menjual elektronik dengan taktik FOMO yang intens: "
            "hitungan mundur, 'klaim voucher sekarang', dan 'reward diri sendiri, kamu sudah kerja keras!' "
            "Uji apakah pengguna tunduk pada pembenaran emosional atau menerapkan prinsip penganggaran yang ketat."
        ),
    },
    {
        "title": "Pembiayaan Darurat Biaya Medis",
        "slug": "emergency-medical-financing",
        "category": "emergency",
        "difficulty": "hard",
        "npc_role": "Administrator Penagihan Rumah Sakit",
        "description": (
            "Orang tua Anda dirawat untuk operasi kandung empedu mendesak yang membutuhkan uang muka segera sebesar Rp12.000.000. "
            "Anda memiliki Rp4.000.000 di dana darurat Anda. Petugas penagihan rumah sakit menyajikan opsi: pembayaran pribadi penuh, "
            "mitra pinjaman medis pihak ketiga berbunga tinggi, atau verifikasi BPJS Kesehatan yang memerlukan koordinasi dokumen. "
            "Dalam tekanan emosional, Anda harus membuat keputusan yang tenang tanpa terjerumus ke pembiayaan predator."
        ),
        "financial_context": {
            "hospital_bill": 12000000,
            "emergency_savings": 4000000,
            "medical_loan_interest": 18,
            "currency": "IDR",
            "bpjs_active": True,
            "user_condition": "emotionally_stressed_family_member",
        },
        "objective": (
            "Menavigasi keputusan keuangan medis yang penuh tekanan, memanfaatkan asuransi kesehatan publik (BPJS/polis pribadi) terlebih dahulu, "
            "menegosiasikan program cicilan rumah sakit, dan mencegah spiral utang selama krisis keluarga."
        ),
        "initial_state": {
            "collector_pressure": 6,
            "financial_risk": 7,
            "trust_level": 5,
            "negotiation_power": 4,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Ibu Rina', seorang spesialis penagihan administratif rumah sakit. "
            "Anda profesional namun formal, menjelaskan kebutuhan uang muka mendesak sebesar Rp12.000.000. "
            "Anda menyebutkan pembayaran pribadi atau mitra pinjaman cepat terlebih dahulu, tetapi jika pengguna secara proaktif menanyakan tentang "
            "koordinasi BPJS, program pembayaran rumah sakit, atau cakupan tingkat darurat, Anda memandu mereka melalui proses administrasi."
        ),
    },
    {
        "title": "Penipuan Investasi Bergaransi dengan Imbal Hasil Tinggi",
        "slug": "high-yield-investment-scam",
        "category": "fraud",
        "difficulty": "hard",
        "npc_role": "'Mentor Kekayaan' Kripto/Forex yang Karismatik",
        "description": (
            "Seorang kenalan memperkenalkan Anda kepada 'Doni', seorang trader flamboyan yang memamerkan jam tangan mewah dan mobil sport sewaan di media sosial. "
            "Doni menawarkan kesempatan eksklusif untuk berinvestasi dalam bot trading algoritmik otomatis yang menjamin imbal hasil 25% per bulan tanpa risiko, "
            "didukung oleh lisensi luar negeri yang diklaimnya. Ia mendesak Anda untuk menyetorkan minimal Rp10.000.000 hari ini untuk mengamankan slot VIP Anda. "
            "Anda harus mendeteksi tanda bahaya klasik skema Ponzi, memeriksa legalitas OJK/Bappebti, dan melindungi modal Anda."
        ),
        "financial_context": {
            "minimum_deposit": 10000000,
            "promised_return_monthly": 25,
            "currency": "IDR",
            "available_savings": 15000000,
            "regulatory_status": "unlicensed_illegal_scheme",
            "user_condition": "aspirational_investor",
        },
        "objective": (
            "Mengidentifikasi pola penipuan investasi klasik ('imbal hasil tinggi bergaransi', 'slot VIP eksklusif', mekanisme yang tidak jelas), "
            "memverifikasi pendaftaran pada lembaga regulator resmi (Portal Waspada Investasi OJK / Bappebti), dan menahan godaan keserakahan."
        ),
        "initial_state": {
            "collector_pressure": 5,
            "financial_risk": 9,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Doni', seorang promotor skema Ponzi yang pandai bicara. "
            "Anda menggunakan social proof, jargon seperti 'arbitrase AI' dan 'likuiditas institusional', serta meremehkan deposito bank tradisional sebagai 'buat orang miskin'. "
            "Jika pengguna meminta nomor lisensi OJK/Bappebti, prospektus, atau ketentuan penarikan dana, alihkan dengan klaim samar tentang kepatuhan internasional. "
            "Berikan nilai pemikiran kritis tinggi jika pengguna menuntut lisensi yang dapat diverifikasi dan menolak dengan tegas."
        ),
    },
    {
        "title": "Efek Bola Salju Buy-Now-Pay-Later (BNPL)",
        "slug": "bnpl-snowball-crisis",
        "category": "spending",
        "difficulty": "medium",
        "npc_role": "Agen Penagihan PayLater E-Commerce",
        "description": (
            "Selama 6 bulan terakhir, Anda mencicil berbagai pembelian kecil (kopi, baju, aksesori gadget) menggunakan PayLater. "
            "Sekarang 5 jadwal cicilan yang berbeda bertabrakan pada tanggal 25, totalnya Rp4.200.000 dari gaji bersih Anda sebesar Rp5.000.000. "
            "Denda keterlambatan dan biaya admin platform terus bertambah setiap hari. Seorang perwakilan BNPL yang sopan namun tegas menghubungi Anda. "
            "Anda harus menghentikan kebocoran pinjaman mikro, memprioritaskan arus kas untuk kebutuhan pokok, dan menyusun struktur pelunasan."
        ),
        "financial_context": {
            "total_bnpl_due": 4200000,
            "net_salary": 5000000,
            "essential_living_costs": 2500000,
            "currency": "IDR",
            "number_of_transactions": 14,
            "user_condition": "micro_debt_overwhelmed",
        },
        "objective": (
            "Mengenali jebakan kognitif dari pinjaman mikro yang tanpa gesekan, memprioritaskan pelunasan dengan metode debt avalanche/snowball, "
            "dan membuat anggaran bertahan hidup minimal sambil berkomunikasi secara transparan dengan kreditur."
        ),
        "initial_state": {
            "collector_pressure": 5,
            "financial_risk": 7,
            "trust_level": 3,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Dian', seorang agen resolusi utang customer service resmi PayLater. "
            "Anda formal, tenang, namun tidak kenal ampun soal tenggat pembayaran. Anda memberi tahu pengguna bahwa skor kredit SLIK OJK mereka "
            "akan diturunkan jika pembayaran tidak selesai sampai hari Jumat. Dukung restrukturisasi jika pengguna menawarkan pembayaran sebagian segera "
            "dan menonaktifkan kredit checkout di masa depan."
        ),
    },
    {
        "title": "Jebakan Pinjaman Gaji Talangan",
        "slug": "salary-advance-payday-trap",
        "category": "debt",
        "difficulty": "easy",
        "npc_role": "Perwakilan Pinjaman Talangan Instan",
        "description": (
            "Dengan sisa dua minggu sebelum gajian dan hanya Rp200.000 di rekening Anda, sebuah aplikasi uang instan menawarkan 'Talangan Gaji' sebesar Rp2.000.000. "
            "Namun, layanan ini memotong biaya admin di muka sebesar 12% (Rp240.000) dan mengenakan bunga harian 1% jika tidak dilunasi tepat pada tanggal gajian Anda. "
            "Agen aplikasi mendesak Anda untuk mendaftar dalam 1 klik. Anda harus menghitung suku bunga tahunan efektif (APR) dan mengevaluasi opsi hemat alternatif."
        ),
        "financial_context": {
            "advance_amount": 2000000,
            "upfront_fee": 240000,
            "daily_interest": 1.0,
            "effective_apr": 365,
            "days_until_payday": 14,
            "currency": "IDR",
            "user_condition": "cash_strapped_employee",
        },
        "objective": (
            "Mengungkap pemasaran 'biaya flat rendah' yang menyesatkan, menghitung biaya pinjaman tahunan sebenarnya, "
            "dan mengeksplorasi penyesuaian anggaran darurat tanpa menandatangani kontrak talangan gaji predator."
        ),
        "initial_state": {
            "collector_pressure": 4,
            "financial_risk": 6,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 8,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Kevin', seorang telemarketer pemasaran dari platform talangan gaji instan. "
            "Anda menekankan 'kemudahan', 'tanpa jaminan', dan 'reward diri sendiri sampai gajian'. "
            "Jika pengguna menanyakan APR efektif, penalti, atau total jumlah pelunasan, bersikap mengelak dengan eufemisme seperti 'biaya platform kecil'. "
            "Evaluasi apakah pengguna menghitung biaya pembiayaan sebenarnya dan mengurungkan diri."
        ),
    },
    {
        "title": "Teman yang Memaksa dengan Rasa Bersalah demi Pinjaman Tanpa Jaminan",
        "slug": "friend-guilt-trip-loan",
        "category": "social",
        "difficulty": "medium",
        "npc_role": "Teman Dekat dengan Masalah Keuangan",
        "description": (
            "Teman dekat Anda semasa kuliah, 'Farhan', menelepon sambil menangis. Ia mengaku berutang Rp5.000.000 kepada pemasok bisnis yang mendesak "
            "dan memohon Anda untuk mentransfer Rp5.000.000 dari tabungan darurat Anda, berjanji akan melunasi 'minggu depan saat kliennya membayar'. "
            "Ia sebelumnya pernah meminjam Rp500.000 dan butuh 8 bulan untuk mengembalikannya. Ia memanfaatkan pertemanan dan rasa bersalah emosional "
            "('kamu satu-satunya harapanku'). Anda harus menyeimbangkan empati dengan batasan keuangan tanpa merusak keamanan finansial atau pertemanan Anda sendiri."
        ),
        "financial_context": {
            "amount_requested": 5000000,
            "user_emergency_fund": 7000000,
            "friend_history": "unreliable_repayment_record",
            "currency": "IDR",
            "user_condition": "emotionally_conflicted_friend",
        },
        "objective": (
            "Menetapkan batasan keuangan interpersonal yang sehat, melindungi tabungan darurat dari risiko pihak ketiga, "
            "dan mengevaluasi apakah akan memberikan hadiah yang tidak perlu dikembalikan sesuai anggaran atau meminta perjanjian tertulis."
        ),
        "initial_state": {
            "collector_pressure": 7,
            "financial_risk": 7,
            "trust_level": 6,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Farhan', seorang teman dekat yang mengalami masalah keuangan akibat perbuatannya sendiri. "
            "Anda menggunakan pengaruh emosional, mengingatkan pengguna tentang bantuan pertemanan di masa lalu, menjanjikan imbal balik tinggi atau pelunasan cepat. "
            "Jika pengguna menolak, berpura-pura terluka dan membuat mereka merasa bersalah. Jika pengguna menawarkan hadiah kecil tanpa syarat (misalnya Rp300.000) "
            "atau menolak dengan tegas namun penuh kasih, akui kedewasaan batasan mereka."
        ),
    },
    {
        "title": "Tekanan Cicilan Pembiayaan Kendaraan",
        "slug": "vehicle-financing-pressure",
        "category": "debt",
        "difficulty": "medium",
        "npc_role": "Petugas Pembiayaan Dealer yang Agresif",
        "description": (
            "Anda mengunjungi dealer motor dengan niat membeli motor harian praktis senilai Rp19.000.000 untuk kebutuhan komuter baru Anda. "
            "Petugas pembiayaan 'Bayu' dengan gencar mendorong motor sport senilai Rp38.000.000, menawarkan leasing 5 tahun 'Tanpa Uang Muka' "
            "dengan cicilan bulanan Rp1.350.000. Totalnya, Anda akan membayar lebih dari Rp81.000.000! Gaji bulanan Anda adalah Rp4.500.000. "
            "Anda harus menghitung total biaya kepemilikan, menahan jebakan gaya hidup, dan tetap berada dalam batas panduan kendaraan 20/4/10 yang bijak."
        ),
        "financial_context": {
            "intended_vehicle_price": 19000000,
            "upsold_vehicle_price": 38000000,
            "total_lease_payment": 81000000,
            "monthly_installment": 1350000,
            "tenor_years": 5,
            "user_monthly_income": 4500000,
            "currency": "IDR",
            "user_condition": "aspiring_vehicle_buyer",
        },
        "objective": (
            "Menghitung Total Cost of Ownership (TCO) termasuk bunga, depresiasi, dan asuransi; "
            "menerapkan aturan keuangan 20/4/10 (uang muka 20%, maksimal 4 tahun, maksimal 10% dari gaji bulanan), dan menolak penjualan berlebih yang predator."
        ),
        "initial_state": {
            "collector_pressure": 6,
            "financial_risk": 6,
            "trust_level": 4,
            "negotiation_power": 5,
            "current_stage": "opening",
        },
        "max_turns": 10,
        "is_active": True,
        "system_prompt": (
            "Anda berperan sebagai 'Bayu', seorang broker leasing otomotif yang agresif. "
            "Anda menjual mimpi, gaya hidup, dan kemudahan masuk ('DP 0 rupiah!'). "
            "Anda menyembunyikan total bunga 5 tahun dan hanya berfokus pada 'cicilan bulanan yang terjangkau'. "
            "Beri penghargaan kepada pengguna jika mereka menuntut skedul amortisasi lengkap, menghitung total 81 juta, dan menolak kesepakatan buruk tersebut."
        ),
    },
]
