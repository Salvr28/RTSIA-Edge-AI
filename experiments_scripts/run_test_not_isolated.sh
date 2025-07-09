#!/bin/bash

# Controlla se è stato fornito esattamente un argomento (il nome del file)
if [ "$#" -ne 1 ]; then
    echo "Errore: Devi specificare il nome del file di output."
    echo "Uso: $0 <percorso_file_output>"
    exit 1
fi

# Assegna il primo argomento alla variabile
output_file="$1"

# Pulisce il file di output se esiste, altrimenti lo crea
> "$output_file"

echo "Avvio di 30 cicli di test. I risultati verranno aggiunti a: $output_file"
echo "----------------------------------------------------"

# Esegue il loop per 30 volte
for i in $(seq 1 30)
do
    echo "[INFO] Inizio esecuzione #$i di 30..."

    # Esegue cyclictest, cattura TUTTO il suo output in una variabile temporanea.
    # Usiamo una variabile temporanea per poter processare l'output in più modi.
    # '2>&1' reindirizza stderr a stdout per catturare tutti i messaggi.
    CYCLICTEST_OUTPUT=$(sudo cyclictest --mlockall --priority=90 --duration=30 2>&1)

    # Estrae il valore 'Max' dall'ultima riga dell'output di cyclictest
    # e lo appende al file di output specificato.
    echo "$CYCLICTEST_OUTPUT" | tail -n 1 | grep "T: 0" | awk '{print $NF}' >> "$output_file"

    echo "[INFO] Esecuzione #$i completata. Valore Max finale salvato in '$output_file'."

    # --- OUTPUT DI DEBUG ---
    echo ""
    echo "[DEBUG] Ultime 3 righe di output di cyclictest per l'esecuzione #$i:"
    echo "--------------------------------------------------"
    echo "$CYCLICTEST_OUTPUT" | tail -n 3
    echo "--------------------------------------------------"

    # --- PULIZIA CACHE ---
    echo "[INFO] Pulizia della cache..."
    sudo sync
    sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
    echo "[INFO] Cache pulita."

    echo ""
    sleep 2
done

echo "----------------------------------------------------"
echo "Test completato. Tutti i 30 risultati sono stati salvati in '$output_file'."