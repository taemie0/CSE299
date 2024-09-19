import "./App.css";
import "./normal.css";
import React, { useState, useEffect } from "react";
import axios from "axios";
// import { HashLoader } from "react-spinners";

function App() {
  //use effect to get models
  // useEffect(() => {
  //   getModels();
  // }, []);

  // need to change the id structure

  const [currentModel, setCurrentModel] = useState("gemma2:2b");

  const updateModelInBackend = (modelId) => {
    // Make the POST request to your Flask backend to update config.yaml
    axios
      .post("http://localhost:5000/update-model", { model_name: modelId })
      .then((response) => {
        console.log("Config updated successfully:", response.data);
        setCurrentModel(modelId); 
      })
      .catch((error) => {
        console.error("Error updating config:", error);
      });
  };

  const [pastConversations, setPastConversations] = useState([
    { title: "Conversation 1", summary: "Summary of conversation 1" },
    { title: "Conversation 2", summary: "Summary of conversation 2" },
    // Add more conversations as needed
  ]);
  const [models, setModels] = useState([
    { id: "gemma2:2b" },
    { id: "mistral:latest" },
    { id: "llama3.1:latest" },
  ]);
  // const [currentModel, setCurrentModel] = useState("gemma2:2b");
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [input, setInput] = useState("");
  const [chatLog, setChatLog] = useState([
    {
      user: "gpt",
      message: "Hello, I am an AI. How can I help you today?",
    },
  ]);

  async function handleSubmit(e) {
    e.preventDefault();
    const startTime = performance.now();
    // await setChatLog([...chatLog, { user: "user", message: `${input}` }]);
    let newChatLog = [...chatLog, { user: "user", message: `${input}` }];
    setInput("");
    setChatLog(newChatLog);
    const messages = newChatLog.map((message) => message.message).join("\n");
    console.log("FRONT message:", messages);
    const response = await fetch("http://localhost:5000/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        // message: chatLog.map((message) => message.message).join(" "),
        message: messages,
        currentModel: currentModel,
      }),
    });
    // Capture the end time after receiving the response
    const endTime = performance.now(); // or Date.now()

    // Calculate the time difference
    const responseTime = endTime - startTime; // In milliseconds

    // Convert milliseconds to minutes
    const responseTimeMinutes = responseTime / 60000;

    // Log the response time in minutes
    console.log(`Response time: ${responseTimeMinutes.toFixed(2)} minutes`);

    const data = await response.json();
    console.log(data);
    setChatLog([...newChatLog, { user: "gpt", message: `${data.message}` }]);
    console.log(data);
  }
  //clear chats

  function clearChat() {
    setChatLog([]);
  }

  // chnange this for getting ollama models from device
  function getModels() {
    fetch("http://localhost:5000/models")
      .then((res) => res.json())
      .then((data) => setModels(data));
    //  .then(data => console.log(data));
  }

  const toggleDrawer = () => {
    setDrawerOpen(!isDrawerOpen);
  };

  return (
    <div className="App">
      {/* Drawer Toggle Button */}
      <button className="drawer-toggle" onClick={toggleDrawer}>
        [=]
      </button>

      {/* Side Menu Drawer */}
      <aside className={`sidemenu ${isDrawerOpen ? "open" : ""}`}>
        <h1>Physics BOT</h1>

        {/* New Chat Button */}
        <div className="side-menu-button" onClick={clearChat}>
          <span>+</span>
          New Chat
        </div>
        <div>
          <h1> </h1>
        </div>

        {/* Model Selector Dropdown */}
        <div className="dropdown dropdown-right side-menu-button w-60 h-13">
          <div tabIndex={0} role="button">
            {currentModel} {/* Display the selected model here */}
          </div>
          <ul
            tabIndex={0}
            className="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow"
          >
            {models.map((model) => (
              <li key={model.id}>
                <a
                  onClick={() => {
                    updateModelInBackend(model.id);
                  }}
                >
                  {model.id}
                </a>
              </li>
            ))}
          </ul>
        </div>
        {/* Past Conversations Grid */}
        <div className="past-conversations absolute grid grid-cols-1 w-56 h-13">
          <h1 className="text-lg font-semibold">Past Conversations</h1>
          {pastConversations.map((conversation, index) => (
            <div
              key={index}
              className="relative  p-4 rounded-lg shadow-md hover:bg-gray-600 transition-colors"
            >
              <button
                //  onClick={() => handleDelete(index)}
                className="absolute top-2 right-2 bg-red-300 text-white p-2 rounded-full opacity-0 hover:opacity-100 transition-opacity"
              >
                ✕
              </button>
              {/* <h3 className="font-semibold">{conversation.title}</h3> */}
              <p className="text-gray-400">{conversation.summary}</p>
            </div>
          ))}
        </div>
      </aside>

      {/* chatbox */}
      <section className="chatbox">
        <div className="chat-log">
          {chatLog.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
        </div>
        <div className="chat-input-holder">
          <form onSubmit={handleSubmit}>
            <input
              rows="1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="chat-input-textarea"
              placeholder="Enter your message..."
            ></input>
          </form>
        </div>
      </section>
    </div>
  );
}

const ChatMessage = ({ message }) => {
  return (
    <div className={`chat-message ${message.user === "gpt" && "chatgpt"}`}>
      <div className="chat-message-center">
        <div className={`avatar ${message.user === "gpt" && "chatgpt"}`}>
          {message.user === "gpt" ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              xmlSpace="preserve"
              width={200}
              height={200}
              fill="#efd1ff"
              stroke="#efd1ff"
              viewBox="0 0 512 512"
            >
              <path d="M512 256c0-38.187-36.574-71.637-94.583-93.355 1.015-6.127 1.894-12.177 2.5-18.091 5.589-54.502-7.168-93.653-35.917-110.251-9.489-5.478-20.378-8.26-32.341-8.26-28.356 0-61.858 16.111-95.428 43.716-27.187-22.434-54.443-37.257-79.275-42.01-4.642-.905-9.105 2.142-9.993 6.776-.879 4.625 2.15 9.096 6.775 9.975 21.282 4.079 45.15 17.109 69.308 36.702-18.278 16.708-36.378 36.651-53.487 59.255-28.561 3.447-55.031 9.088-78.592 16.529-4.395-27.913-4.13-52.813 1.331-72.439 2.321.495 4.71.785 7.168.785 18.825 0 34.133-15.309 34.133-34.133 0-18.816-15.309-34.133-34.133-34.133S85.333 32.384 85.333 51.2c0 10.146 4.531 19.166 11.58 25.429-7.305 23.347-7.996 52.915-2.475 86.067C36.514 184.414 0 217.839 0 256c0 37.12 34.765 70.784 94.447 93.099-10.197 61.107.486 109.516 33.553 128.614 9.489 5.478 20.378 8.252 32.35 8.252 28.382 0 61.918-16.136 95.505-43.785 27.469 22.682 54.733 37.385 79.206 42.078a8.71 8.71 0 0 0 1.613.154c4.011 0 7.595-2.842 8.38-6.921.879-4.634-2.15-9.105-6.776-9.992-20.847-3.994-44.843-16.913-69.308-36.702 18.287-16.708 36.378-36.651 53.487-59.255 28.578-3.456 55.066-9.088 78.626-16.538 4.395 27.887 4.122 52.787-1.365 72.457-2.33-.503-4.719-.794-7.185-.794-18.825 0-34.133 15.317-34.133 34.133 0 18.824 15.309 34.133 34.133 34.133 18.824 0 34.133-15.309 34.133-34.133 0-10.138-4.523-19.149-11.563-25.412 7.339-23.407 8.047-52.966 2.526-86.101C475.52 327.561 512 294.144 512 256zM351.659 43.11c8.934 0 16.947 2.014 23.808 5.973 22.246 12.843 32.265 47.01 27.477 93.73-.478 4.625-1.22 9.395-1.963 14.157-23.518-7.424-49.937-13.047-78.438-16.495-17.041-22.613-35.029-42.675-53.248-59.383 29.551-23.944 58.496-37.982 82.364-37.982zm46.105 131.098c-4.139 19.396-10.266 39.603-18.202 60.186a572.15 572.15 0 0 0-20.087-38.127c-7.313-12.681-15.036-24.815-22.997-36.437 22.041 3.498 42.675 8.379 61.286 14.378zM256.12 92.407c14.507 13.158 28.945 28.552 42.871 45.764A568.501 568.501 0 0 0 256 136.533c-14.669 0-28.988.58-42.914 1.63 13.977-17.229 28.493-32.589 43.034-45.756zm-80.598 67.422a550.996 550.996 0 0 0-22.98 36.446 564.754 564.754 0 0 0-20.096 38.101c-7.987-20.727-14.148-40.986-18.278-60.143 18.636-6.015 39.287-10.896 61.354-14.404zM119.467 34.133c9.412 0 17.067 7.654 17.067 17.067 0 9.412-7.654 17.067-17.067 17.067-9.404 0-17.067-7.654-17.067-17.067 0-9.412 7.663-17.067 17.067-17.067zM17.067 256c0-29.79 31.548-57.088 80.777-75.998 5.359 24.141 13.722 49.758 24.832 75.887-11.264 26.419-19.61 52.113-24.934 76.194C47.283 312.619 17.067 284.774 17.067 256zm238.856 163.576c-13.474-12.169-26.923-26.291-39.927-42.052.734-1.092 1.28-2.295 1.886-3.465 12.766.879 25.557 1.408 38.118 1.408 14.677 0 28.996-.572 42.931-1.63-13.969 17.22-28.484 32.58-43.008 45.739zm57.344-64.299c-18.415 2.031-37.606 3.123-57.267 3.123-11.29 0-22.775-.469-34.261-1.203-.648-18.253-15.59-32.93-34.005-32.93-18.825 0-34.133 15.317-34.133 34.133 0 18.825 15.309 34.133 34.133 34.133 5.547 0 10.726-1.459 15.36-3.823 12.996 15.735 26.334 29.858 39.714 42.129-29.585 23.996-58.573 38.059-82.458 38.059-8.943 0-16.947-2.005-23.817-5.973-25.813-14.899-33.673-55.91-25.404-108.041a381.708 381.708 0 0 0 14.37 4.215c4.523 1.237 9.233-1.451 10.479-5.99a8.524 8.524 0 0 0-5.999-10.47c-5.41-1.476-10.615-3.072-15.701-4.71 4.105-19.123 10.197-39.424 18.185-60.262a560.543 560.543 0 0 0 18.577 35.447 8.524 8.524 0 0 0 7.415 4.301 8.527 8.527 0 0 0 4.224-1.118c4.096-2.33 5.521-7.543 3.183-11.639a526.947 526.947 0 0 1-24.516-48.58 524.582 524.582 0 0 1 25.975-51.268 522.155 522.155 0 0 1 31.42-48.085A525.634 525.634 0 0 1 256 153.602c19.686 0 38.886 1.101 57.327 3.132a530.575 530.575 0 0 1 31.369 48.068 534.44 534.44 0 0 1 25.967 51.106c-7.561 17.101-16.162 34.295-25.975 51.302a522.768 522.768 0 0 1-31.421 48.067zM204.8 358.4c0 4.796-1.997 9.122-5.197 12.22-.043.034-.094.043-.137.077-.051.034-.068.094-.119.137-3.046 2.85-7.117 4.634-11.614 4.634-9.404 0-17.067-7.654-17.067-17.067 0-9.412 7.663-17.067 17.067-17.067 9.413-.001 17.067 7.654 17.067 17.066zm131.686-6.229a549.203 549.203 0 0 0 22.98-36.429c7.313-12.672 13.943-25.472 20.062-38.263 8.021 20.779 14.208 41.079 18.347 60.279-18.645 6.016-39.304 10.905-61.389 14.413zm56.047 125.696c-9.404 0-17.067-7.654-17.067-17.067 0-9.412 7.663-17.067 17.067-17.067 9.412 0 17.067 7.654 17.067 17.067 0 9.412-7.654 17.067-17.067 17.067zm21.709-145.895c-5.376-24.192-13.815-49.877-24.977-76.075 10.991-25.899 19.354-51.516 24.738-75.955 49.314 18.91 80.93 46.234 80.93 76.058 0 29.773-31.505 57.062-80.691 75.972z" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              xmlSpace="preserve"
              width={800}
              height={800}
              viewBox="0 0 60.671 60.671"
            >
              <ellipse
                cx={30.336}
                cy={12.097}
                rx={11.997}
                ry={12.097}
                style={{
                  fill: "#010002",
                }}
              />
              <path
                d="M35.64 30.079H25.031c-7.021 0-12.714 5.739-12.714 12.821v17.771h36.037V42.9c0-7.082-5.693-12.821-12.714-12.821z"
                style={{
                  fill: "#010002",
                }}
              />
            </svg>
          )}
        </div>
        <div className="message">{message.message}</div>
      </div>
    </div>
  );
};

export default App;
