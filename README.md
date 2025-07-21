# progetto-software

Aprire un terminale nella root del progetto ed eseguire:

docker-compose build (al momento impiega quasi 5 minuti a causa, soprattutto, dell'installazione dei pacchetti Node. A volte dà errore durante l'installazione di qualche pacchetto: per risolvere è sufficiente rieseguire il comando)

docker-compose up -d (lancia i container)

docker exec -it sfsc-app python /app/off_chain/main.py (esegue l'applicazione)

(Besu impiega qualche secondo ad avviarsi)

