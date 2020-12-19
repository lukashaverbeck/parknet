# parknet
##### Parkraum optimal nutzen mit autonom kommunizierenden, interaktiven Fahrzeugen

___

## Dokumentation
### Python Konventionen
#### Benennung von Modulen
Python Module, also alle .py-Dateien, sowie Unterordner werden nach dem Prinzip [*Snake Case*](https://en.wikipedia.org/wiki/Snake_case) benannt.

**Beispiel:** *scripts/calculate_pwm.py*

#### Benennung von Klassen
Klassen werden nach dem Prinzip [*Pascal Case*](https://wiki.c2.com/?PascalCase) benannt.

**Beispiel:** *SteeringNet* ([*ai.py*](https://github.com/lukashaverbeck/parknet/blob/master/ai.py#L369))

#### Benennung von Variablen und Funktionen
Variablen und Funktionen werden nach dem Prinzip [*Snake Case*](https://en.wikipedia.org/wiki/Snake_case) benannt.

**Beispiel:** *check_global_permission* ([*interaction.py*](https://github.com/lukashaverbeck/parknet/blob/master/interaction.py#L267))

#### Benennung von Konstanten
Python bietet keine native Möglichkeit, Variablen als Konstanten zu deklarieren. Werte, die dennoch nach Möglichkeit nicht zur Laufzeit überschrieben werden sollen werden daher nach dem Prinzip [*Snake Case*](https://en.wikipedia.org/wiki/Snake_case) in Großbuchstaben benannt, um sie von Variablen zu unterscheiden.

**Beispiel:** *MAX_VELOCITY* ([*constants.py*](https://github.com/lukashaverbeck/parknet/blob/master/constants.py#L14))

#### Dokumentierung von Funktionen
Jede Funktion wird durch einen Python-Docstring dokumentiert, der die folgenden Eigenschaften der Funktion erklärt:

* allgemeine Funktionsweise
* Parameter mit Datentyp und eventuellen Standardwerten
* Rückgabe un Generatorwerte mit Datentyp
* Fehler, die aktiv von der Funktion selbst geworfen werden

Die Art der Dokumentierung folgt im Wesentlichen dem [Google-Standard](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

**Beispiel:** *Driver.steer* ([*vehicle.py*](https://github.com/lukashaverbeck/parknet/blob/master/vehicle.py#L120))
```
def steer(self, angle_diff):
    """ changes the steering angle of the vehicle
        NOTE this method does not move the vehicle's steering axle
        but instead changes the steering internal angle variable

        Args:
            angle_diff (float): desired angle change

        Returns:
            bool: true if the overall angle fit into the fixed constraints - otherwhise false

        Raises:
            TypeError: when trying to change the steering angle by a non-numerical value
    """

    ...
```

### UML Implementations-Diagramm
![UML Diagramm des Softwareentwurfs](./UML.svg "Softwareentwurf")
