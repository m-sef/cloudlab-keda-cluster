const express = require('express');
const os      = require('os');
const app     = express();
const port    = 8080;

let http_requests_total = 0;

app.get('/metrics', (request, response) => {
    const timestamp_ms = Date.now();

    response.set('Content-Type', 'text/plain');
    response.status(200).send(
        `# HELP http_requests_total Total number of HTTP requests\n` +
        `# TYPE http_requests_total counter\n` +
        `http_requests_total ${http_requests_total}\n`
    );
})

app.get('/', (request, response) => {
    http_requests_total += 1;

    const time_ms    = parseFloat(request.query.burn);
    const time_start = Date.now();
    const time_end   = time_start + time_ms;

    let x = 0.0;

    while (Date.now() <= time_end)
    {
        x += Math.sqrt(x + 1);
    }

    console.log(`burn=${time_ms}, ${x}`);

    response.status(200).send('ok\n');
})

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});
