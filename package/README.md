# plex-tvdb-alt-orderer
A utility that applies alternate TVDB orders to Plex.  
It was specifically created to apply the Money Heist Netflix order but can be used for any show/order combination.

_NOTE: A TVDB API subscription is required._

## Usage
### Interactive
By default, this application runs in interactive mode and will prompt the user for all necessary information.
However, all of this information can also be supplied via the CLI or environment variables.

#### Example (User/Password)
```
B:\> plex-tvdb-alt-orderer
[?] Enter your Plex server name (user/password authentication) or URL (token authentication): CoolGuyServer
[?] Enter your Plex username: coolguy
[?] Enter your Plex password: P@$$W0RD
[?] Enter the name of the show: Money Heist
[?] Enter your TVDB subscriber PIN: ABC1234
[?] Select the order to apply: Alternate Order
   Aired Order
   DVD Order
   Absolute Order
 > Alternate Order
   Regional Order
   Alternate DVD Order

Updating Plex |################################| 48/48
```

#### Example (Token)
```
B:\> plex-tvdb-alt-orderer
[?] Enter your Plex server name (user/password authentication) or URL (token authentication): http://127.0.0.1:32400/
[?] Enter your Plex token: a9vuu9aklnKisJy4kmsT
[?] Enter the name of the show: Money Heist
[?] Enter your TVDB subscriber PIN: ABC1234
[?] Select the order to apply: Alternate Order
   Aired Order
   DVD Order
   Absolute Order
 > Alternate Order
   Regional Order
   Alternate DVD Order

Updating Plex |################################| 48/48
```

### CLI
```
Usage: plex-tvdb-alt-orderer [OPTIONS]

Options:
  --plex-library TEXT   Your Plex TV show library name. Omit to use the
                        PLEX_LIBRARY environment variable, choose from a list
                        interactively or if your Plex server has a sole TV
                        show library.
  --plex-password TEXT  Your Plex password. Omit to use the PLEX_PASSWORD
                        environment variable or enter interactively.
  --plex-server TEXT    Your Plex server name (user/password authentication)
                        or URL (token authentication). Omit to use the
                        PLEX_SERVER environment variable or enter
                        interactively.
  --plex-show TEXT      The name of the show in Plex. Omit to use the
                        PLEX_SHOW environment variable or enter interactively.
  --plex-token TEXT     Your Plex token. Omit to use the PLEX_TOKEN
                        environment variable or enter interactively.
  --plex-user TEXT      Your Plex username. Omit to use the PLEX_USER
                        environment variable or enter interactively.
  --tvdb-order TEXT     The TVDB order name (as specified for API-connected
                        systems). Omit to use the TVDB_ORDER environment
                        variable or choose from a list interactively.
  --tvdb-pin TEXT       Your TVDB subscriber PIN. Omit to use the TVDB_PIN
                        environment variable or enter interactively.
  --help                Show this message and exit.
```

#### Example
```
plex-tvdb-alt-orderer --plex-server "CoolGuyServer" --plex-user coolguy --plex-password P@$$W0RD --plex-show "Money Heist" --tvdb-pin ABC1234 --tvdb-order "Alternate Order"
```

### Environment Variables
| Name | Description |
| ------------- | ------------- |
| `PLEX_LIBRARY` | Your Plex TV show library name. |
| `PLEX_PASSWORD` | Your Plex password. |
| `PLEX_SERVER` | Your Plex server name (user/password authentication) or URL (token authentication). |
| `PLEX_SHOW` | The name of the show in Plex. |
| `PLEX_TOKEN` | Your Plex token. |
| `PLEX_USER` | Your Plex username. |
| `TVDB_ORDER` | The TVDB order name (as specified for API-connected systems). |
| `TVDB_PIN` | Your TVDB subscriber PIN. |

_NOTE: CLI parameters take precedence over environment variables._

### Additional Information
If the show name (entered interactively or via the CLI or environment variable) matches multiple Plex shows, the user will be prompted to select one:
```
[?] Select the show to update: The 10th Kingdom
 > The 10th Kingdom
   Animal Kingdom (2016)
   Kingdom
   Kingdom (2014)
   The Last Kingdom
```