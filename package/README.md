# plex-tvdb-alt-orderer
A utility that applies alternate TVDB orders to Plex.  
It was specifically created to apply the Money Heist Netflix order but can be used for any show/order combination.

_NOTE: A TVDB API subscription is required._

## Usage
### Interactive
By default, this application runs in interactive mode and will prompt the user for all necessary information.
However, all of this information can also be supplied via the CLI.

#### Example
```
B:\> plex-tvdb-alt-orderer
[?] Enter your TVDB subscriber PIN: ABC1234
[?] Enter your Plex username: coolguy
[?] Enter your Plex password: P@$$W0RD
[?] Enter your Plex server name: CoolGuyServer
[?] Enter the name of the show: Money Heist
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
  --plex-library TEXT   Your Plex TV show library name. Omit to choose from a
                        list interactively or if your Plex server has a single
                        TV show library.
  --plex-password TEXT  Your Plex password. Omit to enter interactively.
  --plex-server TEXT    Your Plex server name. Omit to enter interactively.
  --plex-show TEXT      The name of the show in Plex. Omit to enter
                        interactively.
  --plex-user TEXT      Your Plex username. Omit to enter interactively.
  --tvdb-order TEXT     The TVDB order name (as specified for API-
                        connected systems). Omit to choose from a list
                        interactively.
  --tvdb-pin TEXT       Your TVDB subscriber PIN. Omit to enter interactively.
  --help                Show this message and exit.
```

#### Example
```
plex-tvdb-alt-orderer --tvdb-pin ABC1234 --plex-user coolguy --plex-password P@$$W0RD --plex-show "Money Heist" --plex-server "CoolGuyServer" --tvdb-order "Alternate Order"
```

### Notes
If the show name (entered interactively or via the CLI) matches multiple Plex shows, the user will be prompted to select one:
```
[?] Select the show to update: The 10th Kingdom
 > The 10th Kingdom
   Animal Kingdom (2016)
   Kingdom
   Kingdom (2014)
   The Last Kingdom
```