import pathlib
import sys

# directory reach
directory = str(pathlib.Path(__file__).parent.parent.resolve())

# setting path
sys.path.append(directory)

from SpacedRepetition import SpacedRepetition


db_name = "testdb" #, number_of_boxes = 7, records_per_box = 5
db = SpacedRepetition(db_name)


db.AddRecord("", "lasting for a very short time", "ephemeral")

db.AddRecord("", "atrakcyjny, uwodzący", "alluring, enticing, captivating")

db.AddRecord("", "hipnotyzujący", "mesmerizing")

db.AddRecord("", "niewypowiedziane, nieznane", "innefable")

db.AddRecord("", "overwhelmingly fearful", "petrified")

db.AddRecord("", "a countless or extremally great number", "myriad")

db.AddRecord("","person showing ability to speak fluently and coherently", "articulate")

db.AddRecord("","nunchi", "the subtle art and ability to listen and gauge others' moods, it means 'eye force/power'")

db.AddRecord("", "Anton Chekhov, The Duel", "In the search for truth human beings take 2 steps forward and one step back. Suffering, mistakes and weariness of life thrust them back, but the thirst for truth and stubborn will will drive the forward. And who knows? Perhaps they will find the real truth at last.")

db.AddRecord("", "4 virtues of Mencius", "benevolence, justice, courtesy, knowledge")

db.AddRecord("", "Oumi Janta quote, Senegalese skate dancer", "If I can see you grove - if you have fun - I can see that you trully feel the music and feel the track. - And that makes you move much more beautiful.")

db.AddRecord("", "Pale Blue Dot monologue by Carl Sagan (part 1)", "From this distant vantage point, the Earth might not seem of any particular interest. But for us, it's different. Consider again that dot. That's here. That's home. That's us. On it everyone you love, everyone you know, everyone you ever heard of, every human being who ever was, lived out their lives. The aggregate of our joy and suffering, thousands of confident religions, ideologies, and economic doctrines, every hunter and forager, every hero and coward, every creator and destroyer of civilization, every king and peasant, every young couple in love, every mother and father, hopeful child, inventor and explorer, every teacher of morals, every corrupt politician, every 'superstar', every 'supreme leader', every saint and sinner in the history of our species lived there on a mote of dust suspended in a sunbeam.")

db.AddRecord("", "Pale Blue Dot monologue by Carl Sagan (part 2)", "The Earth is a very small stage in a vast cosmic arena. Think of the rivers of blood spilled by all those generals and emperors so that, in glory and triumph, they could become the momentary masters of a fraction of a dot. Think of the endless cruelties visited by the inhabitants of one corner of this pixel on the scarcely distinguishable inhabitants of some other corner, how frequent their misunderstandings, how eager they are to kill one another, how fervent their hatreds.")

db.AddRecord("", "Pale Blue Dot monologue by Carl Sagan (part 3)", "Our posturings, our imagined self-importance, the delusion that we have some privileged position in the Universe, are challenged by this point of pale light. Our planet is a lonely speck in the great enveloping cosmic dark. In our obscurity, in all this vastness, there is no hint that help will come from elsewhere to save us from ourselves.")

db.AddRecord("", "Pale Blue Dot monologue by Carl Sagan (part 4)", "The Earth is the only world known so far to harbor life. There is nowhere else, at least in the near future, to which our species could migrate. Visit, yes. Settle, not yet. Like it or not, for the moment the Earth is where we make our stand.")

db.AddRecord("", "Pale Blue Dot monologue by Carl Sagan (part 5)", "It has been said that astronomy is a humbling and character-building experience. There is perhaps no better demonstration of the folly of human conceits than this distant image of our tiny world. To me, it underscores our responsibility to deal more kindly with one another, and to preserve and cherish the pale blue dot, the only home we've ever known.")

db.AddRecord("", "5 great filters of propaganda system by Noam Chomsky, Edward Herman", "1. the size, concentrated ownership, owner wealth and profit orientation of the dominant media firms; 2. advertising as the primary source of finances of mass media; 3. the reliance of media on sources approved by those primary sources and agents of power; 4. 'flak' as means of disciplining the media; 5. 'anticommunism' as national religion and control mechanism")

db.AddRecord("", "V for Vendetta, Shakespear quote", "Beneath this mask there is more than flash... beneath this mask there is an idea, Mr. Creedy... and ideas are bulletproof.")

db.AddRecord("", "Francois Chollet on inteligence testing", "Inteligence is not ability to solve known problems, but to use the learned knowledge to solve novel problems. In short perfect test would be an extrapolation of learned solutions of problems to solve novel or extrapolated problem")

db.AddRecord("", "Francois Chollet on human individual", "Everything about ourselves is echo of the past and echo of people who lived before us.")

db.AddRecord("", "Three aspects of Yin&Yang", "1. fostering yang while reppeling ying; 2. blending Yin and Yang; 3. transcending Ying and Yang")

db.AddRecord("", "Shopenhauer o błędach w osądzaniu", "Błędne sądy zdarzają się nader często, błędne wnioski zaś nader rzadko.")

db.AddRecord("", "Gabor Mate 'us and them'", "It is only a habit of our egocentric mind that divides the world into 'us and them'. More precisely, it is our inability - or refusal - to see the 'us' in 'them' and them in what we take to be 'us'.")

db.AddRecord("", "Understanding Reality - the taoist aim", "THe Taoist aim is to open conciousness and therby allowing greater access to reality, bypassing mental habit, stabilising concious knowing by real knowledge so that it is not subject to distortng influences.")

db.AddRecord("", "Shakespear, Oh wonder quote from Tempest", "Oh, wonder! How many godly creatures are there here! How beauteous mankind is! O brave new world, that has such people in 't.")

db.AddRecord("", "Martian quote at the end by Mark Watney ( Matt Damon)", "This is the end. Now,, you can either accept that or you can get to work. That's all there is, you just begin. You do math, you solve one problem and then you solve the next one. And then the next. And if you solve enough problems, you get to home.")

db.AddRecord("", "Mustafa Mond quote on the idea behind soma", "It was that sort of idea that might easily decondition the more unsettled minds among the high castes - make them lose the faight in happiness as the Sovereign Good and take to believing instead, that the goal was somewhere beyond. [...] What fun is would be if one didn't have to think about happiness.")

db.AddRecord("", "Mortimer Adler, How to Read a Book, quote about taking others' opinions", "It is the most distinctive mark of philosophical questions that everyone must answer them for himself. Taking the opinions of others is not solving them, but avading them.")

db.AddRecord("", "Plato quote #1", "All learning has an emotional base.")

db.AddRecord("", "Social topics", "race; crime; law enforcement; poverty; education; welfare; war and peace; government; organization of social power; kinds of property and ownership; distribution of wealth")

db.AddRecord("", "Jargon of social science", "culture (cross, counter, sub); in-group; alienation; status; input/output; infrastructure; ethnic; behavioral; consensus")

db.AddRecord("", "Mortimer Adler quote #1 on understanding book", "You cannot understand a book if you refuse to hear what it is saying.")

db.AddRecord("", "Rutger Bregman quote  #1 on scholarship", "The fruits of the scholarship fall well outside the tunnel vision of the scarcity mindset.")

db.AddRecord("", "Master Keaton's skunks joke", "Once there were two little skunks named In and Out. Sometimes In and Out played outside and sometimes they played inside. One day In was out and Out was in. Mother skunk told Out to go Out and bring In in. So Out wnet out and in a few minutes he came in with In. Mother skunk was quite astonished with her young skunk. 'My-my', Out!' - she said - 'How in the world you found In so quickly?' Out just smiled up at mother skunk and said - 'In-stinked'")



