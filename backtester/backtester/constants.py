#main error codes
HTTP_401_INVALID_CREDENTIALS = 401
HTTP_402_STRATEGY_ALREADY_RUNNING = 402
HTTP_STRATEGY_RUNNING_SUCCESS = 201


ERROR_MESSAGE_USER_NOT_FOUND = 'User is Invalid/Expired'
STRATEGY_RUNNING_MESSAGE = 'Strategy Running..!'
EMAIL_NOT_SPECIFIED = 'Request Type of email not specified'
ERROR_MESSAGE_STRATEGY_ALREADY_RUNNING = 'Strategy already running please Square off it first to run another Strategy..!'

#final response message
ERROR_HTTP_INVALID_CREDENTIALS ={'error':{'code': HTTP_401_INVALID_CREDENTIALS, 'field': 'email/password', 'error_message': ERROR_MESSAGE_USER_NOT_FOUND}}
ERROR_HTTP_EMAIL_NOT_SPECIFIED ={'error': {'code':HTTP_401_INVALID_CREDENTIALS,  'field': 'Email', 'error_message': EMAIL_NOT_SPECIFIED}}
STRATEGY_SUCCESS_HTTP_MESSAGE ={'error': {'code':HTTP_STRATEGY_RUNNING_SUCCESS,  'field': 'Strategy', 'error_message': STRATEGY_RUNNING_MESSAGE}}
ERROR_HTTP_STRATEGY_ALREADY_RUNNING ={'error': {'code':HTTP_402_STRATEGY_ALREADY_RUNNING,  'field': 'Strategy Running', 'error_message': ERROR_MESSAGE_STRATEGY_ALREADY_RUNNING}}

user_type = [
    ('SuperAdmin', 'SuperAdmin'),
    ('Customer', 'Customer'),
]

strategy_status = [
    ('Running', 'Running'),
    ('Saved', 'Saved'),
    ('Stopped', 'Stopped'),
]

option_status = [
    ('option_buying', 'option_buying'),
    ('option_selling', 'option_selling'),
]

order_type = [
    ('BUY', 'BUY'),
    ('SELL', 'SELL'),
]

SELECTION_TYPE = [
    ('atm_point', 'atm_point'),
    ('closest_premium', 'closest_premium'),
]

call_put = [
    ('PE', 'PE'),
    ('CE', 'CE'),
]

ORDER_ENTRY_EXIT = [
    ('entry', 'entry'),
    ('book_profit', 'book_profit'),
    ('exit', 'exit'),
]

ENTRY_EXIT_REASON = [
    ('direct_entry', 'direct_entry'),
    ('wt_entry', 'wt_entry'),
    ('wt_group_entry', 'wt_group_entry'),
    ('group_entry', 'group_entry'),
    ('re_entry', 're_entry'),
    ('direct_exit', 'direct_exit'),
    ('group_exit', 'group_exit'),
    ('premium_exit', 'premium_exit'),
    ('mtom_exit', 'mtom_exit'),
]

ORDER_STATUS = [
    ('success', 'Success'),
    ('rejected', 'Rejected'),
    ('pending', 'Pending'),
]

type = [
    ('OptionBuying', 'OptionBuying'),
    ('OptionSelling', 'OptionSelling'),
]

candle_size = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('5', '5'),
    ('10', '10'),
    ('15', '15'),
]

buffer_type_choices=[
    ('POINTS','POINTS'),
    ('PERCENTAGE','PERCENTAGE'),]

indicators_type_choices=[
    ('EMA',"EMA"),
    ('SMA','SMA'),
    ('DEMA','DEMA'),
    ('TRIMA','TRIMA')
    # ('HMA','HMA')
]

sl_count_choices=[
    ('High/Low','High/Low'),
    ('POINTS','POINTS'),
    ('PERCENTAGE','PERCENTAGE'),
]

target_count_choices= [
    ('Multiplier','Multiplier'),
    ('POINTS','POINTS'),
    ('PERCENTAGE','PERCENTAGE'),
]

candle_size_choices=[
    ('PERCENTAGE','PERCENTAGE'),
    ('POINTS','POINTS'),
]


SEGMENT_TYPE = [
    ('cash', 'cash'),
    ('future', 'future'),
    ('option', 'option'),
]

OPTION_TYPE = [
    ('CE', 'CE'),
    ('PE', 'PE'),
]

trade_type_choice = [
    ('BANKNIFTY', 'BANKNIFTY'),
    ('NIFTY', 'NIFTY'),
    ('FINNIFTY', 'FINNIFTY'),
]

position_type_choice = [
    ('ATM', 'ATM'), 
    ('OTM', 'OTM'), 
    ('ITM', 'ITM'), 
]

CLOSEST_PREMIUM_TYPE = [
    ('near', 'near'), 
    ('greater', 'greater'),
    ('less', 'less'),
]

TARGET_TYPE = [
    ('PERCENTAGE', 'PERCENTAGE'), 
    ('POINTS', 'POINTS'), 
]

TARGET_UP_DOWN = [
    ('UP', 'UP'), 
    ('DOWN', 'DOWN'), 
]

TARGET_ON = [
    ('spot', 'spot'), 
    ('premium', 'premium'), 
]

WANDT_TRADE_STATUS = [
    ('pending', 'pending'), 
    ('entry', 'entry'),
    ('exit', 'exit'),
    ('re_entry', 're_entry'),
]

INSTRUMENT_PRODUCT_TYPE = [
    ('NRML', 'NRML'), 
    ('MIS', 'MIS'), 
    ('CNC', 'CNC'), 
]

WANDT_INSTRUMENT_PRODUCT_TYPE = [
    ('NRML', 'NRML'), 
    ('MIS', 'MIS'),
]

INSTRUMENT_IDS = [
    (256265, "NIFTY"),
    (260105, "BANKNIFTY"),
    (257801, "FINNIFTY"),
]

STRICK_DISTANCE_GAP = [
    (50, "NIFTY"),
    (100, "BANKNIFTY_FINNIFTY"),
]

STRATEGY_TYPE_CHOICES=[
    ('Bullish','Bullish'),
    ('Bearish','Bearish'),
    ('Non_Directional','Non_Directional')
]