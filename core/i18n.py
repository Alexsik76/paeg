"""
Internationalization (i18n) support for the Electronic Voting Simulator.
"""

from typing import Dict


# Dictionary keys
class T:
    # UI Elements
    APP_TITLE = "app_title"
    CONTROL_PANEL = "control_panel"
    TERMINAL_LOGS = "terminal_logs"
    RESULTS = "results"
    SELECT_LAB = "select_lab"
    SELECT_LANGUAGE = "select_language"
    VOTE_SETTINGS = "vote_settings"
    SELECT_SCENARIO = "select_scenario"
    SELECT_CANDIDATE = "select_candidate"
    SELECT_VOTER = "select_voter"
    ACTION = "action"
    EXECUTE_SCENARIO = "execute_scenario"
    CLEAR_LOGS = "clear_logs"
    PROCESS_TERMINAL_LOG = "process_terminal_log"
    NO_LOGS = "no_logs"
    ELECTION_RESULTS = "election_results"
    NO_VOTES = "no_votes"
    UNREGISTERED_USER = "unregistered_user"
    TIE_WARNING = "tie_warning"
    RESET_VOTES = "reset_votes"
    RESET_CONFIRMATION = "reset_confirmation"
    CANCEL = "cancel"
    ELECTION_HELD = "election_held"
    ELECTION_NOT_HELD = "election_not_held"
    TASKS = "tasks"
    LAB_PREFIX = "lab_prefix"

    # Scenarios (These map from config.yaml IDs)
    SCENARIO_NORMAL = "scenario_normal"
    SCENARIO_DOUBLE = "scenario_double"
    SCENARIO_UNREGISTERED = "scenario_unregistered"
    SCENARIO_TAMPERED = "scenario_tampered"
    SCENARIO_SIMULATE_ALL = "scenario_simulate_all"

    # Protocol Logs
    CVK_INIT = "cvk_init"
    VOTER_PREPARING = "voter_preparing"
    SENDING_PAYLOAD = "sending_payload"
    RECEIVED_PAYLOAD = "received_payload"
    DECRYPTED_SUCCESS = "decrypted_success"
    ERR_SIGNATURE = "err_signature"
    SIG_VERIFIED = "sig_verified"
    ERR_UNREGISTERED = "err_unregistered"
    ERR_DOUBLE_VOTE = "err_double_vote"
    WARN_UNKNOWN_CAND = "warn_unknown_cand"
    VOTE_TALLIED = "vote_tallied"
    ERR_PROCESS_VOTE = "err_process_vote"
    ATTEMPT_1 = "attempt_1"
    ATTEMPT_2 = "attempt_2"
    SIMULATING_ALL = "simulating_all"
    SIMULATION_OK = "simulation_ok"
    SIMULATION_ERRORS = "simulation_errors"

    # Lab 2: Blind Signature Protocol
    SCENARIO_NORMAL_BLIND = "scenario_normal_blind"
    SCENARIO_SIMULATE_ALL_BLIND = "scenario_simulate_all_blind"
    SCENARIO_DOUBLE_REQUEST_BLIND = "scenario_double_request_blind"
    SCENARIO_DOUBLE_VOTE_BLIND = "scenario_double_vote_blind"
    SCENARIO_TAMPERED_BLIND = "scenario_tampered_blind"

    BLIND_PREPARING_SETS = "blind_preparing_sets"
    BLIND_SENDING_SETS = "blind_sending_sets"
    BLIND_CVK_REQUEST_MULT = "blind_cvk_request_mult"
    BLIND_VOTER_SEND_MULT = "blind_voter_send_mult"
    BLIND_CVK_SIGNED = "blind_cvk_signed"
    BLIND_CVK_REJECTED = "blind_cvk_rejected"
    BLIND_CVK_ALREADY_SIGNED = "blind_cvk_already_signed"
    BLIND_UNBLINDING = "blind_unblinding"
    BLIND_CASTING_VOTE = "blind_casting_vote"
    BLIND_CAST_SECOND_VOTE = "blind_cast_second_vote"
    BLIND_ERR_ID_USED = "blind_err_id_used"
    BLIND_ERR_TAMPERED = "blind_err_tampered"
    CVK_INIT_BLIND = "cvk_init_blind"

    # Lab 3: Split Protocol
    SCENARIO_NORMAL_SPLIT = "scenario_normal_split"
    SCENARIO_SIMULATE_ALL_SPLIT = "scenario_simulate_all_split"
    SCENARIO_DOUBLE_RN_SPLIT = "scenario_double_rn_split"
    SCENARIO_DOUBLE_VOTE_SPLIT = "scenario_double_vote_split"
    SCENARIO_INVALID_RN_SPLIT = "scenario_invalid_rn_split"
    SCENARIO_VERIFY_SPLIT = "scenario_verify_split"

    SPLIT_SIMULATING_ALL = "split_simulating_all"
    SPLIT_BR_INIT = "split_br_init"
    SPLIT_CVK_INIT = "split_cvk_init"
    SPLIT_VOTER_REQUESTS_RN = "split_voter_requests_rn"
    SPLIT_BR_ISSUED_RN = "split_br_issued_rn"
    SPLIT_ERR_DOUBLE_RN = "split_err_double_rn"
    SPLIT_VOTER_VOTING = "split_voter_voting"
    SPLIT_VOTER_FAKE_RN = "split_voter_fake_rn"
    SPLIT_VOTER_VERIFICATION = "split_voter_verification"
    SPLIT_VERIFY_SUCCESS = "split_verify_success"
    SPLIT_VERIFY_FAIL_MISMATCH = "split_verify_fail_mismatch"
    SPLIT_VERIFY_FAIL_NOT_FOUND = "split_verify_fail_not_found"
    ERR_INVALID_RN = "err_invalid_rn"
    ERR_RN_ALREADY_USED = "err_rn_already_used"


# Translations
translations: Dict[str, Dict[str, str]] = {
    "English": {
        T.APP_TITLE: "Simulation:",
        T.CONTROL_PANEL: "Control Panel",
        T.TERMINAL_LOGS: "Terminal Logs",
        T.RESULTS: "Results",
        T.TASKS: "Tasks",
        T.LAB_PREFIX: "Lab",
        T.SELECT_LAB: "Select Lab Protocol",
        T.SELECT_LANGUAGE: "Language / Мова",
        T.VOTE_SETTINGS: "Vote Settings",
        T.SELECT_SCENARIO: "Select Scenario",
        T.SELECT_CANDIDATE: "Select Candidate to Vote For",
        T.SELECT_VOTER: "Select Voter",
        T.ACTION: "Action",
        T.EXECUTE_SCENARIO: "Execute Scenario",
        T.CLEAR_LOGS: "Clear Logs",
        T.PROCESS_TERMINAL_LOG: "### Process Terminal Log",
        T.NO_LOGS: "No actions logged yet.",
        T.ELECTION_RESULTS: "### Election Results",
        T.NO_VOTES: "No votes have been cast yet or no candidates available.",
        T.UNREGISTERED_USER: "unregistered_user",
        T.TIE_WARNING: "**Tie Detected:** Candidates have an equal number of votes. A run-off election may be required.",
        T.RESET_VOTES: "Reset Election Results",
        T.RESET_CONFIRMATION: "Are you sure? This will delete all current votes and logs.",
        T.CANCEL: "Cancel",
        T.ELECTION_HELD: "✅ Voting Conducted",
        T.ELECTION_NOT_HELD: "Voting Not Conducted",
        T.SCENARIO_NORMAL: "Normal Vote (1 Voter)",
        T.SCENARIO_DOUBLE: "Double Voting Attempt",
        T.SCENARIO_UNREGISTERED: "Unregistered Voter Attempt",
        T.SCENARIO_TAMPERED: "Tampered Ballot Attempt",
        T.SCENARIO_SIMULATE_ALL: "Simulate Full Election (All Voters)",
        T.CVK_INIT: "CVK initialized Simple Protocol.",
        T.VOTER_PREPARING: "Voter {voter} is preparing ballot for {candidate}...",
        T.SENDING_PAYLOAD: "Sending encrypted payload to CVK...",
        T.RECEIVED_PAYLOAD: "Received encrypted vote payload.",
        T.DECRYPTED_SUCCESS: "Payload decrypted successfully with CVK private key.",
        T.ERR_SIGNATURE: "ERROR: Signature verification failed. Possible tampered ballot.",
        T.SIG_VERIFIED: "Signature verified successfully.",
        T.ERR_UNREGISTERED: "ERROR: Unregistered voter {voter} attempted to vote.",
        T.ERR_DOUBLE_VOTE: "ERROR: Voter {voter} attempted to vote twice.",
        T.WARN_UNKNOWN_CAND: "WARNING: Vote cast for unknown candidate {candidate}.",
        T.VOTE_TALLIED: "Vote successfully tallied for voter {voter}.",
        T.ERR_PROCESS_VOTE: "ERROR: Failed to process vote: {error}",
        T.ATTEMPT_1: "Attempt 1/2:",
        T.ATTEMPT_2: "Attempt 2/2 (Double vote):",
        T.SIMULATING_ALL: "--- Simulating full election for all registered voters ---",
        T.SIMULATION_OK: "Full election simulation completed. All {count} votes processed successfully.",
        T.SIMULATION_ERRORS: "WARNING: Full election simulation completed with violations. {success_count} of {total_count} votes tallied.",
        T.SCENARIO_NORMAL_BLIND: "Normal Vote with Blind Signature",
        T.SCENARIO_SIMULATE_ALL_BLIND: "Simulate Full Election (Blind)",
        T.SCENARIO_DOUBLE_REQUEST_BLIND: "Double Signature Request Attempt",
        T.SCENARIO_DOUBLE_VOTE_BLIND: "Double Voting Attempt (Same ID)",
        T.SCENARIO_TAMPERED_BLIND: "Tampered Ballot Attempt (9/10 Check)",
        T.BLIND_PREPARING_SETS: "Voter {voter} generated 10 blinded ballot sets with ID {voter_rnd_id}...",
        T.BLIND_SENDING_SETS: "Sending 10 blinded sets to CVK...",
        T.BLIND_CVK_REQUEST_MULT: "CVK requests unblinding multipliers for 9 random sets to verify...",
        T.BLIND_VOTER_SEND_MULT: "Voter provides multipliers for the requested 9 sets...",
        T.BLIND_CVK_SIGNED: "CVK verified 9 sets successfully. Blind-signed the remaining 1 set.",
        T.BLIND_CVK_REJECTED: "ERROR: CVK found discrepancies in the 9 sets. Signature request rejected.",
        T.BLIND_CVK_ALREADY_SIGNED: "ERROR: CVK has already issued a signature to voter {voter}. Duplicate request rejected.",
        T.BLIND_UNBLINDING: "Voter received signed blinded ballot from CVK. Unblinding...",
        T.BLIND_CASTING_VOTE: "Casting decrypted signed vote for candidate {candidate}...",
        T.BLIND_CAST_SECOND_VOTE: "Attempting to cast another ballot from the same signed set...",
        T.BLIND_ERR_ID_USED: "ERROR: Ballot with ID {voter_rnd_id} was already used. Vote rejected.",
        T.BLIND_ERR_TAMPERED: "ERROR: Ballot signature is invalid. Vote rejected.",
        T.CVK_INIT_BLIND: "CVK initialized Blind Signature Protocol.",
        T.SCENARIO_NORMAL_SPLIT: "Normal Vote (Split Powers)",
        T.SCENARIO_SIMULATE_ALL_SPLIT: "Simulate Full Election (Split)",
        T.SCENARIO_DOUBLE_RN_SPLIT: "Double RN Request Attempt",
        T.SCENARIO_DOUBLE_VOTE_SPLIT: "Double Voting Attempt (Same RN)",
        T.SCENARIO_INVALID_RN_SPLIT: "Invalid RN Usage Attempt",
        T.SCENARIO_VERIFY_SPLIT: "Vote Verification Attempt",
        T.SPLIT_SIMULATING_ALL: "--- Simulating full election (Distribution of Powers) ---",
        T.SPLIT_BR_INIT: "Registration Bureau initialized.",
        T.SPLIT_CVK_INIT: "CVK initialized Split Protocol.",
        T.SPLIT_VOTER_REQUESTS_RN: "Voter {voter} requests Registration Number from Bureau...",
        T.SPLIT_BR_ISSUED_RN: "Bureau issued secret Registration Number to {voter}.",
        T.SPLIT_ERR_DOUBLE_RN: "ERROR: Bureau rejected request. Voter {voter} already has an RN.",
        T.SPLIT_VOTER_VOTING: "Voter {voter} generates anonymous ID and signs ballot...",
        T.SPLIT_VOTER_FAKE_RN: "Voter {voter} generates a fake unauthorized RN...",
        T.SPLIT_VOTER_VERIFICATION: "Voter opens CVK's publicly published ballot list to verify their vote...",
        T.SPLIT_VERIFY_SUCCESS: "✅ VERIFIED: Voter successfully found their anonymous ID. Vote registered correctly for {cand}.",
        T.SPLIT_VERIFY_FAIL_MISMATCH: "❌ VERIFICATION FAILED: Found anonymous ID but candidate does not match!",
        T.SPLIT_VERIFY_FAIL_NOT_FOUND: "❌ VERIFICATION FAILED: Anonymous ID not found in published CVK ballots.",
        T.ERR_INVALID_RN: "ERROR: Registration Number is invalid or not issued by Bureau.",
        T.ERR_RN_ALREADY_USED: "ERROR: Registration Number was already used. Vote rejected.",
    },
    "Українська": {
        T.APP_TITLE: "Симуляція:",
        T.CONTROL_PANEL: "Панель керування",
        T.TERMINAL_LOGS: "Логи (Термінал)",
        T.RESULTS: "Результати",
        T.TASKS: "Завдання",
        T.LAB_PREFIX: "Лабораторна",
        T.SELECT_LAB: "Оберіть протокол",
        T.SELECT_LANGUAGE: "Language / Мова",
        T.VOTE_SETTINGS: "Налаштування голосування",
        T.SELECT_SCENARIO: "Оберіть сценарій",
        T.SELECT_CANDIDATE: "Оберіть кандидата",
        T.SELECT_VOTER: "Оберіть виборця",
        T.ACTION: "Дія",
        T.EXECUTE_SCENARIO: "Виконати сценарій",
        T.CLEAR_LOGS: "Очистити логи",
        T.PROCESS_TERMINAL_LOG: "### Лог виконання протоколу",
        T.NO_LOGS: "Дії ще не фіксувалися.",
        T.ELECTION_RESULTS: "### Результати виборів",
        T.NO_VOTES: "Жодного голосу ще не віддано або кандидати відсутні.",
        T.UNREGISTERED_USER: "незареєстрований_користувач",
        T.TIE_WARNING: "**Увага:** Виявлено однакову кількість голосів. Потреба в повторному голосуванні.",
        T.RESET_VOTES: "Скинути результати виборів",
        T.RESET_CONFIRMATION: "Ви впевнені? Це видалить усі поточні голоси та логи процесу.",
        T.CANCEL: "Скасувати",
        T.ELECTION_HELD: "✅ Голосування проведено",
        T.ELECTION_NOT_HELD: "Голосування не проводилось",
        T.SCENARIO_NORMAL: "Нормальне голосування (1 виборець)",
        T.SCENARIO_DOUBLE: "Спроба подвійного голосування",
        T.SCENARIO_UNREGISTERED: "Спроба голосув. незареєстрованого виборця",
        T.SCENARIO_TAMPERED: "Спроба підміни бюлетеня (пошкоджений бюлетень)",
        T.SCENARIO_SIMULATE_ALL: "Симулювати повні вибори (всі виборці)",
        T.CVK_INIT: "ЦВК ініціалізувала простий протокол.",
        T.VOTER_PREPARING: "Виборець {voter} готує бюлетень за {candidate}...",
        T.SENDING_PAYLOAD: "Надсилання зашифрованого повідомлення з ЕЦП до ЦВК...",
        T.RECEIVED_PAYLOAD: "Отримано зашифрований бюлетень.",
        T.DECRYPTED_SUCCESS: "Повідомлення успішно розшифровано закритим ключем ЦВК.",
        T.ERR_SIGNATURE: "ПОМИЛКА: Перевірка ЕЦП не пройдена. Можлива підміна бюлетеня.",
        T.SIG_VERIFIED: "ЕЦП успішно перевірено відкритим ключем виборця.",
        T.ERR_UNREGISTERED: "ПОМИЛКА: Незареєстрований виборець {voter} спробував проголосувати.",
        T.ERR_DOUBLE_VOTE: "ПОМИЛКА: Виборець {voter} спробував проголосувати двічі.",
        T.WARN_UNKNOWN_CAND: "ПОПЕРЕДЖЕННЯ: Віддано голос за невідомого кандидата {candidate}.",
        T.VOTE_TALLIED: "Голос виборця {voter} успішно зараховано.",
        T.ERR_PROCESS_VOTE: "ПОМИЛКА: Не вдалося опрацювати бюлетень: {error}",
        T.ATTEMPT_1: "Спроба 1/2:",
        T.ATTEMPT_2: "Спроба 2/2 (Подвійне голосування):",
        T.SIMULATING_ALL: "--- Симуляція повних виборів для всіх зареєстрованих виборців ---",
        T.SIMULATION_OK: "Симуляцію виборів завершено. Усі {count} голосів успішно зараховано ЦВК.",
        T.SIMULATION_ERRORS: "ПОПЕРЕДЖЕННЯ: Симуляцію виборів завершено з порушеннями. Зараховано {success_count} з {total_count} голосів.",
        T.SCENARIO_NORMAL_BLIND: "Нормальне голосування (Сліпий підпис)",
        T.SCENARIO_SIMULATE_ALL_BLIND: "Симулювати повні вибори (Сліпий підпис)",
        T.SCENARIO_DOUBLE_REQUEST_BLIND: "Спроба подвійного запиту на підпис",
        T.SCENARIO_DOUBLE_VOTE_BLIND: "Спроба подвійного голосування (той самий ID)",
        T.SCENARIO_TAMPERED_BLIND: "Спроба підміни під час перевірки 9 з 10",
        T.BLIND_PREPARING_SETS: "Виборець {voter} згенерував 10 наборів замаскованих бюлетенів з ID {voter_rnd_id}...",
        T.BLIND_SENDING_SETS: "Надсилання 10 замаскованих наборів до ЦВК...",
        T.BLIND_CVK_REQUEST_MULT: "ЦВК запитує множники для 9 випадкових наборів для перевірки...",
        T.BLIND_VOTER_SEND_MULT: "Виборець надає множники для 9 обраних наборів...",
        T.BLIND_CVK_SIGNED: "ЦВК успішно перевірила 9 наборів і підписала 10-й замаскований набір.",
        T.BLIND_CVK_REJECTED: "ПОМИЛКА: ЦВК виявила маніпуляції у 9 наборах. У підписі відмовлено.",
        T.BLIND_CVK_ALREADY_SIGNED: "ПОМИЛКА: Виборець {voter} вже отримав підпис. Повторний запит відхилено.",
        T.BLIND_UNBLINDING: "Виборець отримав підписані бюлетені. Зняття маскування...",
        T.BLIND_CASTING_VOTE: "Відправка розшифрованого підписаного бюлетеня за кандидата {candidate}...",
        T.BLIND_CAST_SECOND_VOTE: "Спроба відправити інший бюлетень з того ж самого підписаного набору...",
        T.BLIND_ERR_ID_USED: "ПОМИЛКА: Бюлетень з ID {voter_rnd_id} вже був використаний. Голос відхилено.",
        T.BLIND_ERR_TAMPERED: "ПОМИЛКА: Недійсний підпис бюлетеня. Голос відхилено.",
        T.CVK_INIT_BLIND: "ЦВК ініціалізувала протокол сліпого підпису.",
        T.SCENARIO_NORMAL_SPLIT: "Нормальне голосування (Розподіл)",
        T.SCENARIO_SIMULATE_ALL_SPLIT: "Симулювати повні вибори (Розподіл)",
        T.SCENARIO_DOUBLE_RN_SPLIT: "Спроба отримання двох RN",
        T.SCENARIO_DOUBLE_VOTE_SPLIT: "Спроба подвійного голосування (той самий RN)",
        T.SCENARIO_INVALID_RN_SPLIT: "Спроба використання недійсного RN",
        T.SCENARIO_VERIFY_SPLIT: "Перевірка свого голосу виборцем",
        T.SPLIT_SIMULATING_ALL: "--- Симуляція повних виборів (Розподіл повноважень) ---",
        T.SPLIT_BR_INIT: "Бюро реєстрації (БР) ініціалізовано.",
        T.SPLIT_CVK_INIT: "ЦВК ініціалізувала протокол Розподілу Повноважень.",
        T.SPLIT_VOTER_REQUESTS_RN: "Виборець {voter} запитує реєстраційний номер (RN) у Бюро...",
        T.SPLIT_BR_ISSUED_RN: "Бюро реєстрації видало секретний RN для {voter}.",
        T.SPLIT_ERR_DOUBLE_RN: "ПОМИЛКА: Бюро відхилило запит. Виборець {voter} вже отримував RN.",
        T.SPLIT_VOTER_VOTING: "Виборець {voter} генерує анонімний ID та підписує бюлетень...",
        T.SPLIT_VOTER_FAKE_RN: "Виборець {voter} генерує несправжній RN...",
        T.SPLIT_VOTER_VERIFICATION: "Виборець відкриває публічний список опублікованих бюлетенів ЦВК для перевірки...",
        T.SPLIT_VERIFY_SUCCESS: "✅ ПІДТВЕРДЖЕНО: Виборець успішно знайшов свій анонімний ID. Голос за {cand} зараховано вірно.",
        T.SPLIT_VERIFY_FAIL_MISMATCH: "❌ ПЕРЕВІРКА ПРОВАЛЕНА: Анонімний ID знайдено, але кандидат не збігається!",
        T.SPLIT_VERIFY_FAIL_NOT_FOUND: "❌ ПЕРЕВІРКА ПРОВАЛЕНА: Анонімний ID не знайдено в опублікованих списках ЦВК.",
        T.ERR_INVALID_RN: "ПОМИЛКА: ЦВК відхилила бюлетень. RN недійсний (не видавався Бюро).",
        T.ERR_RN_ALREADY_USED: "ПОМИЛКА: ЦВК відхилила бюлетень. Цей RN вже був використаний.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """
    Get translated string for the given key and language.
    Supports string formatting via kwargs.
    """
    lang_dict = translations.get(lang, translations["English"])
    text = lang_dict.get(key, translations["English"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
