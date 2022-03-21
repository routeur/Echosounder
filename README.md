# Echosounder :anchor:

## Présentation 

Echosounder est un explorateur de réseau local proposant une visualisation par graph

Le cycle du pentest est composé de 5 phases : 
 - reconnaissance
 - intrusion
 - élévation de privilège
 - maintient dans le système d'information (backdooring)
 - Exfiltration de donnée sensibles

Echosounder se place dans la phase de reconnaissance de ce cycle, en proposant une fois un accès à un réseau privé obtenu, la possibilité de l'explorer, et de sortir une visualisation dudit réseau.

## Screenshots

![echosounder](https://user-images.githubusercontent.com/16328515/156616053-babeb847-7833-4153-a007-5190cb0f9724.png)

### Ce que Echosounder permet

 - Effectuer des scan d'un réseau local
 - Obtenir une vue clair des réseaux locaux & distants liés à ce réseau local
 - Identifier des machines sur les réseaux
 - Identifier des services sur ces machines
 - Avoir l'ensemble des machines et des réseaux affichés sur un graph
 - Avoir l'ensemble des données de machines et de réseaux dans un panel "data"
 - Exporter les graphs en JSON
 - Importer les graphs en JSON

### Ce que Echosounder n'est pas

 - Un remplaçant à nmap (Echosounder utilise nmap comme dépendance)
 - Un logiciel de "management des asset" (Echosounder ne propose que de la visualisation)
 - Un logiciel de "vulnerability assessement" (Echosounder identifie des services via nmap, mais ne vérifie pas des vulnérabilités)

## Installation

### Dépendances
 
 - nmap (https://nmap.org/)
 - Scapy (https://scapy.net/)
 - Impacket (https://github.com/SecureAuthCorp/impacket)
 - dnspython (https://www.dnspython.org/)

### Installation 

```bash
sudo apt install nmap
sudo pip3 install -r requirements.txt
# mise à jour de la base de donnée CIDR -> AS
python3 asinfo/collectas.py
```

