import socket

HOST        = '127.0.0.1'
PORT        = 9999
BUFFER_SIZE = 1024

clienti_conectati = {}
mesaje = {} 

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("=" * 50)
print(f"  SERVER UDP pornit pe {HOST}:{PORT}")
print("  Asteptam mesaje de la clienti...")
print("=" * 50)

while True:
    try:
        date_brute, adresa_client = server_socket.recvfrom(BUFFER_SIZE)
        mesaj_primit = date_brute.decode('utf-8').strip()

        parti = mesaj_primit.split(' ', 1)
        comanda = parti[0].upper()
        argumente = parti[1] if len(parti) > 1 else ''

        print(f"\n[PRIMIT] De la {adresa_client}: '{mesaj_primit}'")

        if comanda == 'CONNECT':
            if adresa_client in clienti_conectati:
                raspuns = "EROARE: Esti deja conectat la server"
            else:
                clienti_conectati[adresa_client] = True
                nr_clienti = len(clienti_conectati)
                raspuns = f"OK: Conectat cu succes. Clienti activi: {nr_clienti}"
                print(f"[SERVER] Client nou conectat: {adresa_client}")

        elif comanda == 'DISCONNECT':
            if adresa_client in clienti_conectati:
                del clienti_conectati[adresa_client]
                raspuns = "OK: Deconectat cu succes"
                print(f"[SERVER] Client deconectat: {adresa_client}")
            else:
                raspuns = "EROARE: Nu esti conectat la server."

        elif comanda in ['PUBLISH', 'DELETE', 'LIST'] and adresa_client not in clienti_conectati:
            raspuns = "EROARE: Actiune nepermisa. Necesita conectare."

        elif comanda == 'PUBLISH':
            if not argumente:
                raspuns = "EROARE: Mesajul nu poate fi gol."
            else:
                mesaje[urmatorul_id] = {'autor': adresa_client, 'text': argumente}
                raspuns = f"OK: Mesaj publicat cu ID={urmatorul_id}"
                urmatorul_id += 1

        elif comanda == 'DELETE':
            if not argumente.isdigit():
                raspuns = "EROARE: ID-ul trebuie sa fie un numar intreg valid."
            else:
                id_mesaj = int(argumente)
                if id_mesaj not in mesaje:
                    raspuns = f"EROARE: Mesajul cu ID={id_mesaj} nu a fost gasit."
                elif mesaje[id_mesaj]['autor'] != adresa_client:
                    raspuns = "EROARE: Nu ai permisiunea de a sterge acest mesaj pentru ca nu esti autorul"
                else:
                    del mesaje[id_mesaj]
                    raspuns = f"OK: Mesajul cu ID={id_mesaj} a fost sters cu succes."

        elif comanda == 'LIST':
            if not mesaje:
                raspuns = "Nu exista mesaje publicate pe server"
            else:
                raspuns = "Mesaje publicate:\n" + "\n".join([f"  [{m_id}] {date_msg['text']}" for m_id, date_msg in mesaje.items()])

        else:
            raspuns = f"EROARE: Comanda '{comanda}' este necunoscuta. Comenzi valide: CONNECT, DISCONNECT, PUBLISH, DELETE, LIST"

        server_socket.sendto(raspuns.encode('utf-8'), adresa_client)
        print(f"[TRIMIS]  Catre {adresa_client}: '{raspuns}'")

    except KeyboardInterrupt:
        print("\n[SERVER] Oprire server in curs")
        break
    except Exception as e:
        print(f"[EROARE] {e}")

server_socket.close()
print("[SERVER] Socket inchis.")