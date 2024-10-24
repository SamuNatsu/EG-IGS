const htmlToNode = (html) => {
  const tmp = document.createElement('template');
  tmp.innerHTML = html;
  return tmp.content.firstChild;
};

const renderDescription = (desc) =>
  htmlToNode(
    `<details><summary>Product Description</summary>${desc}</details>`
  );
const renderDebug = (title, content) =>
  htmlToNode(
    `<details><summary style="color:blue">ℹ️ ${title}</summary>${content}</details>`
  );
const renderMessage = (result, title, content) =>
  htmlToNode(
    `<details><summary style="color:${
      typeof result === 'boolean' ? (result ? 'green' : 'red') : 'orange'
    }">🤖 ${title}</summary>${content}</details>`
  );
const renderResult = (cost, target) =>
  htmlToNode(
    `<p><b>Costs:</b> ${cost}<br /><b>Target concept:</b> ${target.replaceAll(
      '-',
      ' » '
    )}</p>`
  );

document.querySelector('#search').addEventListener('submit', function (ev) {
  ev.preventDefault();

  const model = this.querySelector('#model').value;
  const method = this.querySelector('#method').value;
  const link = this.querySelector('#link').value;

  const url = new URL(location.href);
  url.pathname = '/api/igs';
  url.searchParams.append('model', model);
  url.searchParams.append('method', method);
  url.searchParams.append('link', link);

  const rEl = document.querySelector('#result');
  rEl.innerHTML = '';

  const sse = new EventSource(url);
  sse.addEventListener('desc', (ev) => {
    const { content } = JSON.parse(ev.data);
    rEl.append(renderDescription(content), htmlToNode('<hr />'));
  });
  sse.addEventListener('dbg', (ev) => {
    const { title, content } = JSON.parse(ev.data);
    rEl.append(renderDebug(title, content));
  });
  sse.addEventListener('msg', (ev) => {
    const { content } = JSON.parse(ev.data);
    const [question, answer] = content.msg.split('\n');
    rEl.append(renderMessage(content.result, question, answer));
  });
  sse.addEventListener('res', (ev) => {
    const { content } = JSON.parse(ev.data);
    rEl.append(
      htmlToNode('<hr />'),
      renderResult(content.cost, content.target)
    );
    sse.close();
  });
  sse.addEventListener('err', (ev) => {
    const { content } = JSON.parse(ev.data);
    rEl.append(
      htmlToNode('<hr />'),
      htmlToNode(`<p style="color: red">${content}</p>`)
    );
    sse.close();
  });
  sse.addEventListener('error', () => {
    rEl.append(
      htmlToNode('<hr />'),
      htmlToNode('<p style="color: red">SSE error</p>')
    );
    sse.close();
  });
});
