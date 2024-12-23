import serial
from openpyxl import Workbook
import datetime

# Configurer la connexion au port série
arduino_port = "COM3"  # Remplacez par le port série correct (COM3, COM4, etc.)
baud_rate = 9600  # Assurez-vous qu'il correspond au paramètre dans l'Arduino
ser = serial.Serial(arduino_port, baud_rate)

# Créer un nouveau fichier Excel
workbook = Workbook()
sheet = workbook.active
sheet.title = "Données RFID"

# Ajouter des en-têtes dans le fichier Excel
sheet.append(["ID RFID", "Heure", "Statut", "direction","duration_in"])

def calculate_duration(last_time, current_time):
    """Calculer la durée entre deux temps."""
    last_time_obj = datetime.datetime.strptime(last_time, "%H:%M:%S")
    current_time_obj = datetime.datetime.strptime(current_time, "%H:%M:%S")
    duration = (current_time_obj - last_time_obj).total_seconds()
    return max(duration, 0)

print("Lecture des données depuis Arduino. Appuyez sur Ctrl+C pour arrêter.")
scan_count=0
duration_in=0
try:
    while True:
        # Lire les données du port série
        data = ser.readline().decode('utf-8').strip()

        # Assurer que la ligne contient les données au bon format
        if "ID RFID:" in data and "Heure:" in data and "Statut:" in data:
            # Extraire les données
            parts = data.split("\t")
            id_rfid = parts[0].split("ID RFID: ")[1].strip()
            heure = parts[1].split("Heure: ")[1].strip()
            statut = parts[2].split("Statut: ")[1].strip()
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            # Afficher les données
            if (statut == "Code Verified"):
                scan_count += 1
            if (statut == "Code Not Verified"):
                direction = "dinied"
            elif scan_count % 2 == 0:
                direction = "Sortie"
            else:
                direction = "Entrée"
            
            
            if (direction == "Sortie" and statut == "Code Verified"):
                duration_in = calculate_duration(last_time, current_time)
                
            # Enregistrer dans Excel
            if (statut == "Code Verified"):
                print(f"{id_rfid}\t{current_time}\t{statut}\t{direction}\t{duration_in}")
                sheet.append([id_rfid, current_time, statut, direction, duration_in])
                last_time=current_time
                if direction == "Sortie":
                    duration_in=0
            else:
                print(f"{id_rfid}\t{current_time}\t{statut}\t{direction}\t0")
                sheet.append([id_rfid, current_time, statut, direction, "0"])
            workbook.save("Données_RFID.xlsx")
            
except KeyboardInterrupt:
    print("\nArrêt du programme.")
    ser.close()
    workbook.save("Données_RFID.xlsx")
    print("Les données ont été enregistrées dans 'Données_RFID.xlsx'.")
