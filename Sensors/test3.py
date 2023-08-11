try:
    print([1,2]**2)
except ZeroDivisionError:
    print("divided by 0")
except Exception as e:
    print("except", str(e))
