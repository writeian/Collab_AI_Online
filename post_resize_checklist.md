# Post-Resize Checklist

## After your droplet is resized, run these commands:

### 1. Test the new memory capacity
```bash
free -h
```

### 2. Update your .env file for the larger model
```bash
# For 8GB droplet - use llama2:7b
sed -i 's/OLLAMA_MODEL=.*/OLLAMA_MODEL=llama2:7b/' .env

# For 16GB droplet - use llama2:13b or llama2:70b
# sed -i 's/OLLAMA_MODEL=.*/OLLAMA_MODEL=llama2:13b/' .env
```

### 3. Test the AI connection
```bash
python test_ai_connection.py
```

### 4. Pull additional models if needed
```bash
# For 8GB droplet
ollama pull llama2:7b

# For 16GB droplet
ollama pull llama2:13b
# or
ollama pull llama2:70b
```

### 5. Start your application
```bash
python app.py
```

## Expected Results:
- ✅ AI responses should work properly
- ✅ No more memory errors
- ✅ Faster response times
- ✅ Better model quality 