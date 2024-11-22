
./bin/ollama serve &

pid=$!

sleep 5


echo "Pulling llama3 model"
ollama pull smollm2


wait $pid
