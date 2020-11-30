<script>
  export let name;
  import { onMount } from "svelte";
  let messageInput;
  let messages = [];
  let inputText = "";

  onMount(() => {
    messageInput.focus();
  });

  let counter = 0;
  let numUsers = 0;
  const ws = new WebSocket("ws://127.0.0.1:6789");

  ws.onopen = function () {
    console.log("Websocket client connected");
  };

  ws.onmessage = function (e) {
    let data = JSON.parse(e.data);
    if (data.type == "msg") {
      console.log("Received: " + data.texto);
      if (data.texto.slice(0,2) == "* "){
        messages = [...messages, data.texto.slice(2)];
      } else {
        messages = [...messages, "Recebido: " + data.texto];
      }
      inputText = "";
    } else if (data.type == "users") {
      numUsers = data.count;
    } else {
      console.error("unsupported event", data);
    }
  };
  
  function handleClick() {
    messages = [...messages, "Enviado: " + inputText];
    ws.send(JSON.stringify({ msg: inputText }));
    inputText = "";
  }


</script>

<style>
  * {
    box-sizing: border-box;
  }

  main {
    text-align: center;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  h1 {
    color: #1c33fa;
    text-transform: none;
    font-size: 3em;
    font-weight: 100;
    margin: 0 auto;
  }

  .state {
    color: #00bd00;
    font-size: 1.5em;
  }

  @media (min-width: 640px) {
    main {
      max-width: none;
    }
  }

  .chatbox {
    width: 100%;
    height: 59vh;
    padding: 0 1em;
    text-align: left;
    background-color: #eee;
    overflow-y: scroll;
    overscroll-behavior-y: contain;
    scroll-snap-type: y proximity;
  }

  .chatbox p {
    margin-top: 0.3em;
    margin-bottom: 0;
    padding-bottom: 0.3em;
  }

  .chatbox > p:last-child {
    scroll-snap-align: end;
  }

  .inputbox {
    display: flex;
    margin-top: 0.5em;
  }

  .inputbox input {
    flex-grow: 1;
  }
</style>

<main>
  <h1><b>{name}</b></h1>
  <p>
    PMR3412: Redes Industriais (2020) - Entrega 2<br>
    Exercício 2: Sala de Bate Papo com WebSockets<br>
    Autor: Pedro Orii Antonacio - nUSP 10333504
  </p>

  <div class="state">
    <span class="users">{numUsers} {numUsers > 1 ? 'users' : 'user'}</span>
    online<br>
  </div>

  <p>
  </p>

  <div class="chatbox">
    {#each messages as message}
      <p>{message}</p>
    {/each}
  </div>
  <form class="inputbox">
    <input type="text" bind:this={messageInput} bind:value={inputText} />
    <button type="submit" on:click|preventDefault={handleClick}>Send</button>
  </form>
</main>
