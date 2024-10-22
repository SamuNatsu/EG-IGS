const htmlToNode = (html) => {
  const tmp = document.createElement('template');
  tmp.innerHTML = html;
  return tmp.content.firstChild;
};

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
    const desc = JSON.parse(ev.data);

    const el = htmlToNode(
      `<details><summary>Product Description</summary>${desc}</details>`
    );
    rEl.append(el, htmlToNode('<hr />'));
  });
  sse.addEventListener('msg', (ev) => {
    const { result, msg } = JSON.parse(ev.data);
    const [q, a] = msg.split('\n');

    const el = htmlToNode(
      `<details><summary style="color:${
        typeof result === 'boolean' ? (result ? 'green' : 'red') : 'orange'
      }">${q}</summary>${a}</details>`
    );
    rEl.append(el);
  });
  sse.addEventListener('result', (ev) => {
    const { cost, target } = JSON.parse(ev.data);

    rEl.append(htmlToNode('<hr />'));
    const el = htmlToNode(
      `<p><b>Costs:</b> ${cost}<br /><b>Target concept:</b> ${target.replaceAll(
        '-',
        ' » '
      )}</p>`
    );
    rEl.append(el);

    sse.close();
  });
  sse.addEventListener('err', (ev) => {
    const err = JSON.parse(ev.data);

    rEl.append(htmlToNode('<hr />'));
    const el = htmlToNode(`<p style="color: red">${err}</p>`);
    rEl.append(el);

    sse.close();
  });
  sse.addEventListener('error', () => {
    rEl.append(htmlToNode('<hr />'));
    const el = htmlToNode('<p style="color: red">SSE error</p>');
    rEl.append(el);

    sse.close();
  });
});
