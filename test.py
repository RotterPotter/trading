import functions 
from datetime import datetime 

if __name__ == "__main__":
  print(functions.take_parameters(datetime.strptime("2004.06.11,13:45", "%Y.%m.%d,%H:%M"), "data.csv"))