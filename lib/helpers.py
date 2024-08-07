import datetime

def coerce_bool_input(inpt, default=False):
    coerced = inpt.strip().lower()
    if coerced == "y" or coerced == "yes":
        b = True
    elif coerced == "n" or coerced == "no" or coerced == "":
        b = False
    else:
        print("Didn't understand response, defaulting to no")
        b = False
    return b

def process_time_str(inpt):
    hour, minute = inpt.split(':')
    return datetime.time(int(hour), int(minute))
