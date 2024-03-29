# -*- coding: UTF-8 -*-
##
##// CURRENT:
##// list of topics by {TOPIC:[["TITLE", "URL"]]}
##
##// FUTURE:
##////list of topics by {TOPIC:[["TITLE", "URL", "TAGS"],
##////                          ["TITLE", "URL", "TAGS"]]}






def Content():
##    //             Suggest Branches for next steps
##    //             If liked: Matplotlib, link to data analysis or Pandas maybe
##    //             If liked: GUI stuff: Kivy, PyGame, Tkinter
##    //             if liked: Text and word-based: NLTK


    # MAIN : [TITLE, URL, BODY_TEXT (LIST), HINTS(LIST)]
    TOPIC_DICT = {"Server":[[u'故障处理',"/server-issue-handle/",[""]],
                            ["Print Function and Strings","/python-tutorial-print-function-strings/",["The Print function outputs text to the console (black area). Let's try it out!","print() is a function, which does something with parameters, and parameters go inside the parenthesis.","See if you can use the print function to output 'Hello!' to the console!"]],
                            ["Math with Python","/math-basics-python-3-beginner-tutorial/"],
                            ["Variables","/python-3-variables-tutorial/"],
                            ["While Loop","/python-3-loop-tutorial/"],
                            ["For Loop","/loop-python-3-basics-tutorial/"],
                            ["Python 2to3 for Converting Python 2 scripts to Python 3","/converting-python2-to-python3-2to3/"]],
                  
                  
                  "Network":[["Intro and environment creation","/flask-web-development-introduction/"],
                           ["Basics, init.py, and your first Flask App!","/creating-first-flask-web-app/"],
                           ["Incorporating Variables and some Logic","/templates-flask-variables-html/"],
                           ["Using Bootstrap to make things pretty","/flask-bootstrap/"],
                           ["Using javascript plugins, with a Highcharts example","/adding-js-plugins-flask-highcharts-example/"],
                           ["Incorporating extends for templates","/flask-template-extends/"],],

                  
                  "Inventory":[["Intro to MySQL","/mysql-intro/"],
                           ["Creating Tables and Inserting Data with MySQL","/create-mysql-tables-insert/"],
                           ["Update, Select, and Delete with MySQL","/mysql-update-select-delete/"],
                           ["Inserting Variable Data with MySQL","/mysql-insert-variable/"],
                           ["Streaming Tweets from Twitter to Database","/mysql-live-database-example-streaming-data/"],],


                  
                            }


    return TOPIC_DICT








if __name__ == "__main__":
    x = Content()

    print(x["Basics"])

    for each in x["Basics"]:
        print(each[1])