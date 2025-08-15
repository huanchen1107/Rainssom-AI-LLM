# 步驟一：建立 Python 環境

您可以選擇以下任一方式建立專案所需的 Python 環境：

**使用 Conda（推薦）若沒有安裝Anaconda 請先安裝 https://www.anaconda.com/download/success**

```bash
conda env create -f environment.yml
conda activate contextual
```

**或使用 pip**

```bash
pip install -r requirements.txt
```

---

# 步驟二：從 Ollama 下載 Llama 3 8B 或 70B 模型

首先，您需要在您的電腦上擁有 `llama3:8b` 這個模型。請打開您的終端機，執行以下指令：

```bash
ollama pull llama3:8b
```

**或下載 Llama 3 70B 的量化模型**

下載網址：
https://huggingface.co/unsloth/Llama-3.3-70B-Instruct-GGUF/resolve/main/Llama-3.3-70B-Instruct-UD-IQ3_XXS.gguf?download=true

---

## 下載 70B 量化模型後的安裝步驟（可選）

### Linux 用戶

1. **建立 Modelfile**
   在專案資料夾（例如 `~/Desktop/my chat robot/`）建立一個名為 `Modelfile` 的純文字檔案（無副檔名），內容如下：
   
   ```
   FROM ~/Downloads/Llama-3.3-70B-Instruct-UD-IQ3_XXS.gguf
   ```
   ⚠️ 請將路徑改為您實際存放 .gguf 檔案的位置。

2. **用 Ollama 建立模型**
   
   ```bash
   cd ~/Desktop/my\ chat\ robot/
   ollama create llama3-70b-final -f ./Modelfile
   ```

### Windows 用戶

1. **建立 Modelfile**
   在專案資料夾（例如 `C:\Users\你的名稱\Desktop\my chat robot\`）建立一個名為 `Modelfile` 的純文字檔案，內容如下：
   
   ```
   FROM C:/Users/你的名稱/Downloads/Llama-3.3-70B-Instruct-UD-IQ3_XXS.gguf
   ```
   ⚠️ 請將路徑改為您實際存放 .gguf 檔案的位置。

2. **用 Ollama 建立模型**
   
   ```powershell
   cd "C:\Users\你的名稱\Desktop\my chat robot"
   ollama create llama3-70b-final -f .\Modelfile
   ```

Ollama 會開始處理您下載的 .gguf 檔案，這個過程需要幾分鐘，請靜待它顯示 success。

---

# 步驟三：執行主程式

完成前述步驟後，您可以使用以下指令啟動主程式：

```bash
streamlit run app.py
```

**或使用以下指令跑 70B 的 Llama3 量化模型（顯存需求 28GB）**

```bash
streamlit run app70b.py
```