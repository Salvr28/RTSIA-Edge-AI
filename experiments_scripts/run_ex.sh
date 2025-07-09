#!/bin/bash

# ---------------------- WORKLOAD AI ------------------------

# Controlla che siano stati forniti gli argomenti necessari
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <percorso_al_file_config.yaml> <nome_file_output_medie.txt>"
    echo "Esempio: $0 /opt/edge_ai_apps/configs/image_classification.yaml final_avg_inference_times_mobilenetv2.txt"
    exit 1
fi

# Percorso al file di configurazione (primo argomento)
CONFIG_FILE="$1"
# Nome del file di output per le medie finali (secondo argomento)
OUTPUT_FILE="$2"

# Percorso allo script Python principale (app_edgeai.py)
APP_EDGEAI_PATH="/opt/edge_ai_apps/apps_python/app_edgeai.py"

# Directory dei log temporanei
LOG_DIR="/tmp/edge_ai_logs"
mkdir -p "$LOG_DIR" # Crea la directory se non esiste

# Numero di iterazioni desiderate
NUM_ITERATIONS=30

# Durata della sleep in secondi
SLEEP_DURATION=5

# Controlla se il file di configurazione esiste
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "ERRORE: Il file di configurazione '$CONFIG_FILE' non esiste."
    exit 1
fi

# Pulisci il file di output precedente, se esiste
> "$OUTPUT_FILE"

echo "Avvio delle $NUM_ITERATIONS iterazioni..."
echo "Le medie finali verranno salvate in $OUTPUT_FILE"

for i in $(seq 1 $NUM_ITERATIONS); do
    echo "--- Inizio Iterazione $i/$NUM_ITERATIONS ---"

    # Nome del file di log per questa iterazione
    PERFORMANCE_LOG="${LOG_DIR}/performance_iteration_${i}.log"

    echo "Esecuzione di $APP_EDGEAI_PATH con config: $CONFIG_FILE"
    # Esegue app_edgeai.py e reindirizza l'output
    sudo python3 "$APP_EDGEAI_PATH" "$CONFIG_FILE" --no-curses --verbose > "$PERFORMANCE_LOG" 2>&1

    # Verifica se il log di performance è stato creato e contiene dati
    if [[ -s "$PERFORMANCE_LOG" ]]; then
        # Estrae l'ultimo valore di 'avg' dal log di performance
        LAST_AVG=$(grep "Time for 'dl-inference':" "$PERFORMANCE_LOG" | tail -1 | awk '{print $(NF-1)}')

        if [[ -n "$LAST_AVG" ]]; then
            echo "Media finale dell'inferenza per Iterazione $i: ${LAST_AVG} ms"
            echo "${LAST_AVG}" >> "$OUTPUT_FILE"
        else
            echo "ATTENZIONE: Impossibile trovare la media finale dell'inferenza nel log per Iterazione $i."
            echo "N/A" >> "$OUTPUT_FILE" # Segnala un errore nel file di output
        fi
    else
        echo "ERRORE: Il file di log di performance '$PERFORMANCE_LOG' non è stato creato o è vuoto per Iterazione $i."
        echo "ERRORE_LOG_VUOTO" >> "$OUTPUT_FILE"
    fi

    # Svuota la cache (richiede privilegi di root)
    echo "Svuotamento della cache..."
    sudo sync # Sincronizza i dati su disco
    sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
    echo "Cache svuotata."

    # Breve sleep
    if [ $i -lt $NUM_ITERATIONS ]; then # Non fare sleep dopo l'ultima iterazione
        echo "Pausa di $SLEEP_DURATION secondi..."
        sleep "$SLEEP_DURATION"
    fi

    echo "--- Fine Iterazione $i/$NUM_ITERATIONS ---"
    echo ""
done

echo "Tutte le $NUM_ITERATIONS iterazioni completate."
echo "I risultati sono disponibili in $OUTPUT_FILE"
echo "I log dettagliati di ogni iterazione si trovano in $LOG_DIR"