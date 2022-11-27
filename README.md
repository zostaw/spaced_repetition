# spaced_repetition

Spaced Repetition - program with DB storing data to be withdrawn from and then placed in sequence over boxes in order to learn facts or quotes.

## Note from the author

This is my personal practice project.
I started working on it, because I wanted to improve two of my weak spots:

- proficiency in object programming and planning the code,
- poor memory

This is far from being finished, at least for now, but it serves the playground for learning - all the building blocks of the memory learning program are implemented - you can try yourself by cloning the repo - see usage under `Usage DEMO` section.\
There is much more I would like to improve - see `Principles of memorization` and `Next steps`.\

### What I learned

While working on this project I learned the basics of the structure of python classes:

- constructor (__init__) method and how it works together with optional input parameters, other methods, variables - it was interesting to figure out a way to implement optional input parameters while keeping the code readable,
- handling files and databases - especially interesting was writing methods that do not destroy the cohesion of the database,
- implementing getter method - it tought me awereness of types of things, how one entity can change its shape and form upon interaction with other. Python is very flexible with types and one variable can take multiple forms - number of elements in an array can change it's type from None, through int to array. Btw. it's a great metaphore for life  - the changing of one's form dependent on the interaction with the world, the invisible forces playing with her/him.
- ValueErrors - I learned how to keep the consistency of the program by verifying the state of variables before interacting with them in method.\
"Who are you, really?" - we should be asking this question more often...

### Principles of memorization

I. To remember learned material over time, the learned material must be repeated according to forgetting curve\
II. To be able to recall in other setting than the learning setup (computer + keyboard), the learning process must be engaging.\
It must:

- use speech to connect the material with language and speech system;
- use visualization in mind, to connect the material with imagination and recall system;
- use creative mind and real life examples to connect the material with the identity of a person who speaks, with the action and not only a skill of memorization.

### The next steps

1. add voice to the program: reading questions and listening to answers
    -correction for misspelled words, skip option
2. add GUI: either javascript in browser or html5
3. add pictures web search

## Usage demo

You can either import the module to separate python file (see below steps) or you can just execute:

```bash
python SpacedRepetition.py
```

1. innititate session

    ```python
    from SpacedRepetition import SpacedRepetition

    sr = SpacedRepetition(
        session_id = "my_session",
        dataset_name="test_quotes",
        num_of_boxes=7,
        daily_limit=5
    )
    ```

    All parameters are optional:\
                session_id (string): unique session id - allows to track state of db
                                    and API requests\
                dataset_name (string): database is initiated from datasets files,
                                    if not provided - empty database will be created\
                num_of_boxes (int): total number of boxes in rotation\
                daily_limit (int): limit number of records that are added into new box\

    At this point dataset is loaded and records can be viewed:

    ```python
    sr.PrintAllRecords()
    ```

    But learning Boxes are not yet initiated.

2. Start daily learning session

    ```python
    from SpacedRepetition import SpacedRepetition

    sr = SpacedRepetition(
        session_id = "my_session",
        dataset_name="test_quotes",
        num_of_boxes=7,
        daily_limit=5
    )

    sr.EoD_Rotation()

    sr.PlaySession()
    ```

    PlaySession()  initiates interactive learning with the records that are already in the boxes.
    EoD_Rotation is a batch method, that simulates rotation of boxes.\
    If there are no boxes, new one is created.\
    Every call of this method will create a new box and initiate it with some of the unassigned records.\
    The number of records that will be assigned is defined by `daily_limit`, while the maximum number of boxes by `num_of_boxes`.\
    After `num_of_boxes` is reached, the oldest box will be dropped.
