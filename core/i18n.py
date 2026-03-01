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


# Translations
translations: Dict[str, Dict[str, str]] = {
    "English": {
        T.APP_TITLE: "Simulation:",
        T.CONTROL_PANEL: "Control Panel",
        T.TERMINAL_LOGS: "Terminal Logs",
        T.RESULTS: "Results",
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
    },
    "Українська": {
        T.APP_TITLE: "Симуляція:",
        T.CONTROL_PANEL: "Панель керування",
        T.TERMINAL_LOGS: "Логи (Термінал)",
        T.RESULTS: "Результати",
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
