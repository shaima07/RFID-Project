#include <SPI.h>
#include <MFRC522.h>
#include <TimeLib.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN); // Instance de la classe
MFRC522::MIFARE_Key key;

// Init array qui stockera le nouvel NUID
byte nuidPICC[4];

void setup() {
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522

  // Initialiser la clé par défaut
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  Serial.println("Lecteur RFID prêt. En attente de carte...");
}

void loop() {
  // Vérifier si une nouvelle carte est présente
  if (!rfid.PICC_IsNewCardPresent())
    return;

  // Vérifier si la carte peut être lue
  if (!rfid.PICC_ReadCardSerial())
    return;

  // Stocker le NUID dans le tableau `nuidPICC`
  for (byte i = 0; i < 4; i++) {
    nuidPICC[i] = rfid.uid.uidByte[i];
  }

  // Déterminer le statut
  String statut;
  if (nuidPICC[0] == 0xBB && nuidPICC[1] == 0x3A && nuidPICC[2] == 0xC3 && nuidPICC[3] == 0x44) {
    statut = "Code Verified";
  } else {
    statut = "Code Not Verified";
  }

  // Récupérer l'heure actuelle
  String currentTime = String(hour()) + ":" + String(minute()) + ":" + String(second());

  // Envoi structuré sur le port série
  Serial.print("ID RFID: ");
  for (byte i = 0; i < 4; i++) {
    Serial.print(nuidPICC[i], HEX); // Affiche l'ID RFID
    Serial.print(i < 3 ? " " : ""); // Ajouter un espace sauf après le dernier octet
  }
  Serial.print("\tHeure: ");
  Serial.print(currentTime);
  Serial.print("\tStatut: ");
  Serial.println(statut);

  // Arrêter la communication avec la carte
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
