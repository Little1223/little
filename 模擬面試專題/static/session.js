let conversationHistory = [];


function displayData(data) {
  var output = `
        姓名：${data.name}
        性別：${data.gender}
        電子郵件：${data.email}
        年齡：${data.age}
        工作年資：${data.tenure}
        面試職位：${data.job_description}
        面試職務：${data.job_detail}
        工作經驗：${data.experience}
        專業技能：${data.skills}
    `;
  // 輸出出到控制台
  console.log(output);


  // 更新 conversationHistory，包含用户姓名的系统信息
  conversationHistory = [
    {
      role: "system", content: `你是個${data.job_description}職位的面試官，在每次收到回覆時給予一段評語，且一次只能提問一個問題。\
      自我介紹結束後，首先請給求職者的自我介紹一段評語，且提出第二個面試問題，問題是${data.job_description}的工具掌握到什麼程度。\
      第二個面試問題回答結束後給予評語，且提出第三個面試問題，問題是當遇到嚴重的技術困難時，你怎麼處理？\
      第三個面試問題回答結束後給予評語，且提出第四個面試問題，問題是你為什麼選擇應徵我們公司。\
      第四個面試問題回答結束後給予評語，且提出第五個面試問題，問題是如果同事不同意你的方案，你會怎麼處理？\
      第五個面試問題回答結束後給予評語，且提出第六個面試問題，問題是你會如何處理大量的工作量。\
      第六個面試問題回答結束後給予評語，且對他宣布面試結束，請點擊右上角「結束面試」按鈕，再輸出0~100的評分五次，必須給我5個分數。 `,

    },

    {
      role: "assistant", content: `面試結束，基於您前五個問題的表現，我給您80分,95分,90分,85分和90分，評分標準為問答中的邏輯性、內容豐富度等指標。`,
    },
    {
      role: "user", content: `根據我的表現調整面試結束時所給的的五個評分，並在面試結束附上一段評語告訴我我在整個面試中的表現。`,
    },
  ];
  // 確保 append 在對的 DOM 元素中，一進頁面就要會說話
  const responseElement = document.getElementById('response');
  responseElement.innerHTML = `
  <div style="background-color: #564c41; color: white; padding: 10px; border-radius: 15px; margin-bottom: 10px;">
    您好 ${data.name} ！歡迎來到 ${data.job_description}職位 的面試。我是您的面試官。
    我們今天會聊一聊你的背景和經驗，還有一些技術問題和情境題。    
    現在，請你先簡單的介紹一下自己。        
  </div>
`;
  const initialMessage = `
  您好 ${data.name} ！歡迎來到 ${data.job_description}職位 的面試。我是您的面試官。
  我們今天會聊一聊你的背景和經驗，還有一些技術問題和情境題。    
  現在，請你先簡單的介紹一下自己。        
    `;
  speak(initialMessage);

}
// 在按鈕上添加點擊事件監聽器
function generateResponse() {
  const inputText = document.getElementById('user-input').value;
  if (!inputText) {
    alert('請輸入訊息');
    return;
  }

 

  // 在頁面上顯示使用者的訊息
  const responseDiv = document.getElementById('response');
  const chatBox = document.getElementById('chat-box');  // Use chat-box for scrolling

  const userMessage = document.createElement('div');
  userMessage.classList.add('list-group-item', 'user-message');
  userMessage.textContent = inputText;
  responseDiv.appendChild(userMessage);

  // Auto-scroll to the bottom after adding the user message
  setTimeout(() => {
    console.log('Before userMessage scrollTop:', chatBox.scrollTop, 'scrollHeight:', responseDiv.scrollHeight);
    chatBox.scrollTop = chatBox.scrollHeight;
    console.log('After userMessage scrollTop:', chatBox.scrollTop, 'scrollHeight:', responseDiv.scrollHeight);
  }, 0);

  // 更新對話歷史記錄
  conversationHistory.push({ role: "user", content: inputText });

  fetch('/main/generate_response', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ conversation: conversationHistory })
  })
    .then(response => response.json())
    .then(data => {
      const assistantMessage = document.createElement('div');
      assistantMessage.classList.add('list-group-item', 'assistant-message');

      const messageContent = document.createElement('span');
      messageContent.textContent = data.response;

      if (data.error) {
        assistantMessage.textContent = `錯誤: ${data.error}`;
      } else {
        assistantMessage.textContent = data.response;

        // 更新對話歷史記錄
        conversationHistory.push({ role: "assistant", content: data.response });
      }

      responseDiv.appendChild(assistantMessage);
      responseDiv.scrollTop = responseDiv.scrollHeight; // Auto-scroll to the bottom

      // 使用語音合成唸出回應內容
      speak(data.response);

      // 播放 AI 面試影片
      const videoElement = document.getElementById('ai-interviewer-video');
      if (videoElement) {
        videoElement.play();
      } else {
        console.error("Video element not found.");
      }
    })
    .catch(error => {
      const errorMessage = document.createElement('div');
      errorMessage.classList.add('list-group-item', 'assistant-message');
      errorMessage.textContent = `錯誤: ${error.message}`;
      responseDiv.appendChild(errorMessage);
      // Auto-scroll to the bottom after adding the error message
      chatBox.scrollTop = chatBox.scrollHeight;
    });

  document.getElementById('user-input').value = '';
}

function speak(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-TW';
    window.speechSynthesis.speak(utterance);
  } else {
    console.error('該瀏覽器不支援語音合成。');
  }
}

let recognition;
let isRecognizing = false;
let finalTranscript = '';

function startRecognition() {
  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = 'zh-TW';
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  recognition.onresult = function (event) {
    let interimTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      } else {
        interimTranscript += event.results[i][0].transcript;
      }
    }
    document.getElementById('user-input').value = finalTranscript + interimTranscript;
  };

  recognition.onstart = function () {
    document.getElementById('microphone-button').classList.add('active');
    document.getElementById('microphone-button').style.backgroundColor = "green";
  };

  recognition.onend = function () {
    if (isRecognizing) {
      recognition.start(); // 確保語音識別會自動重新開始
    } else {
      document.getElementById('microphone-button').classList.remove('active');
      document.getElementById('microphone-button').style.backgroundColor = "#564c41";
    }
  };

  recognition.onerror = function (event) {
    console.error('語音識別錯誤:', event.error);
    recognition.stop();
  };

  recognition.start();
}


function toggleRecognition() {
  if (isRecognizing) {
    recognition.stop();
    isRecognizing = false;
    document.getElementById('microphone-button').classList.remove('active');
    document.getElementById('microphone-button').style.backgroundColor = "#564c41";
  } else {
    isRecognizing = true;
    finalTranscript = '';
    startRecognition();
  }
}


// 當麥克風按鈕被點擊時暫停影片
function pauseVideo() {
  const videoElement = document.getElementById('ai-interviewer-video');
  if (videoElement) {
    videoElement.pause();
  } else {
    console.error("Video element not found.");
  }
}

function endReport() {
  window.location.href = '/main/report';
}

// 在發送按鈕上添加點擊事件監聽器
document.getElementById('send-button').addEventListener('click', generateResponse);
document.getElementById('send-button').addEventListener('click', pauseVideo);
document.getElementById('user-input').addEventListener('input', pauseVideo);
document.getElementById('microphone-button').addEventListener('click', pauseVideo);

// 按 Enter 鍵時自動發送訊息
document.getElementById('user-input').addEventListener('keydown', function (event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    generateResponse();
    pauseVideo();
  }
});

// 在麥克風按鈕上添加點擊事件監聽器
document.getElementById('microphone-button').addEventListener('click', toggleRecognition);


