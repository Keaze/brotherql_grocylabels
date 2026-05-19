# Brother QL Grocy Label Printer Service

<img src="example.png" alt="Example Label" width="348" height="135">

This project is intended to be a webhook target for [Grocy](https://github.com/grocy/grocy) to print labels to a brother QL label printer. 

Datamatrix or QR codes can be used with Datamatrix being the default. Datamatrix will fit better in smaller labels but I've found aren't as easily read by the Grocy 
barcode reader or by the [Android App](https://github.com/patzly/grocy-android).

Endless label rolls are supported (e.g. `62` label size) in addition to die-cut labels.

## Connecting Grocy

Once you have this running somewhere update your config at `app/data/config.php` to match the following. Presuming that you have this running on localhost at port 8000.

### Query-param endpoint (basic)

```
    // Label printer settings
    Setting('LABEL_PRINTER_WEBHOOK', 'http://127.0.0.1:8000/print');
    Setting('LABEL_PRINTER_RUN_SERVER', true);
    Setting('LABEL_PRINTER_PARAMS', []);
    Setting('LABEL_PRINTER_HOOK_JSON', false);

    Setting('FEATURE_FLAG_LABEL_PRINTER', true);
```

### JSON endpoint (recommended — purchase & due dates)

Use `/print/json/async` to avoid Grocy timeouts. Jobs are queued and sent to the printer sequentially.

```
    Setting('LABEL_PRINTER_WEBHOOK', 'http://127.0.0.1:8000/print/json/async');
    Setting('LABEL_PRINTER_RUN_SERVER', true);
    Setting('LABEL_PRINTER_PARAMS', []);
    Setting('LABEL_PRINTER_HOOK_JSON', true);

    Setting('FEATURE_FLAG_LABEL_PRINTER', true);
```

## Environment Variables

The label size and printer are configured via environmental variables. You can also create a `.env` file instead.

| Variable           | Default               | Description                                                                                   |
| ------------------ | --------------------- | --------------------------------------------------------------------------------------------- |
| LABEL_SIZE         | 62x29                 | See the [brother_ql](https://github.com/pklaus/brother_ql) readme for the names of the labels |
| PRINTER_MODEL      | QL-500                | The printer model. One of the values accepted by brother_ql                                   |
| PRINTER_PATH       | file:///dev/usb/lp1   | Where the printer is found on the system. For network printers use `tcp://printer.address`    |
| BARCODE_FORMAT     | Datamatrix            | `Datamatrix` or `QRCode`                                                                      |
| NAME_FONT          | NotoSerif-Regular.ttf | The file name of the font in the fonts directory                                              |
| NAME_FONT_SIZE     | 48                    | The size of that font                                                                         |
| NAME_MAX_LINES     | 4                     | The maximum number of lines to use for the name                                               |
| DUE_DATE_FONT      | NotoSerif-Regular.ttf | The file name of the font in the fonts directory                                              |
| DUE_DATE_FONT_SIZE | 30                    | The size of that font                                                                         |
| ENDLESS_MARGIN     | 10                    | The top & bottom margin to add when using endless labels                                      |
| PURCHASE_DATE_PREFIX | P                   | Label prefix for the purchase date                                                            |
| DUE_DATE_PREFIX    | D                     | Label prefix for the due/best-before date                                                     |

Included fonts are `NotoSans-Regular.ttf` and `NotoSerif-Regular.ttf`

## Endpoints

### Query-param endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/print` | GET, POST | Print label |
| `/image` | GET | Return label as PNG (no printing) |

Parameters:

| Name      | Use                                 |
| --------- | ------------------------------------|
| product   | name                                |
| battery   | name                                |
| chore     | name                                |
| recipe    | name                                |
| grocycode | the barcode                         |
| due_date  | the text at the bottom of the label |

The name will use whichever parameter is given.

### JSON endpoints

Accept a JSON body matching the Grocy webhook payload (`LABEL_PRINTER_HOOK_JSON = true`). Purchase date and due date are read from `stock_entry`.

| Endpoint | Method | Description |
|---|---|---|
| `/print/json` | POST | Print label (blocks until printed) |
| `/print/json/async` | POST | Enqueue print job, return immediately |
| `/print/test` | POST | Log label values, no printing |
| `/image/json` | POST | Return label as PNG (no printing) |

Example payload:

```json
{
  "product": "Milk",
  "grocycode": "GRCY-P-1",
  "stock_entry": {
    "best_before_date": "2026-06-01",
    "purchased_date": "2026-05-19"
  }
}
```

`/print/json/async` is recommended for Grocy webhooks — it returns `200 OK` immediately and serializes jobs through a queue so the printer is never hit concurrently.

## Running

**Note:** Theres no security on this web service, so don't make it publicly available.

This has been tested with python 3.10, newer may work fine.

You will need to install the `libdmtx` library for the barcodes to generate, see [pylibdmtx](https://pypi.org/project/pylibdmtx/) documentation on pypi.

Its advisable to run and install in a [venv](https://docs.python.org/3/library/venv.html). For example:

```
    # Create and enter the venv
    python -m venv .venv
    source ./.venv/bin/activate
    # Install packages
    python -m pip install -U -r requirements.txt

    # exit with ./.venv/bin/deactivate
```

For development you can use `flask run --debug` to run the service on port 5000. Alternatively use `gunicorn -c gunicorn_conf.py app:app` to run the service on port 8000.

## TODO

- Some more formatting options

### Docker

A Dockerfile is included based on a python 3.10 alpine image. The default port is 8000.

Published to Dockerhub as [sam159/brotherql_grocylabels](https://hub.docker.com/r/sam159/brotherql_grocylabels) for architectures amd64, arm64, and armv7.

As an example, you can launch this with `docker run -d -p 8000:8000 -e PRINTER_MODEL=QL-500 -e PRINTER_PATH=file:///dev/usb/lp1 sam159/brotherql_grocylabels:latest`.

An example `docker-compose.yml` file can be found [here](docker-compose.yml).

## Contributing

I'll try to keep on top of bugs but feature requests may go unfulfilled. Please use the issue tracking in Github.

PRs are welcome!
