package main

import (
	"os"
	"log"
	"github.com/hoisie/web"
	"github.com/newrelic/go-agent/v3/newrelic"
	//"labix.org/v2/mgo"
	//"labix.org/v2/mgo/bson"
	//"fmt"
)

//const (
//	MONGODB_URL = "ts-news-mongo:27017"
//)

//func getNews(val string) string {
//

//	session, err := mgo.Dial(MONGODB_URL)
//	if err != nil {
//		panic(err)
//	}
//	defer session.Close()
//
//	session.SetMode(mgo.Monotonic, true)
//	// db := session.DB("xtest")
//	// collection := db.C("xtest")
//	c := session.DB("xtest").C("xtest")
//

//	 var personAll []News
//	 err = c.Find(nil).All(&personAll)
//	 for i := 0; i < len(personAll); i++ {
//	 	fmt.Println("Person ", personAll[i].Name, personAll[i].Phone)
//	 }
//
//}

type News struct {
	Title   string `bson:"Title"`
	Content string `bson:"Content"`
}

func hello(val string) string {
	// Start New Relic transaction if app is initialized
	if app != nil {
		txn := app.StartTransaction("GET /news")
		defer txn.End()

		// Add custom attributes
		txn.AddAttribute("service", "ts-news-service")
		txn.AddAttribute("endpoint", "/news")
	}

	var str = []byte(`[
                       {"Title": "News Service Complete", "Content": "Congratulations:Your News Service Complete"},
                       {"Title": "Total Ticket System Complete", "Content": "Just a total test"}
                    ]`)
	return string(str)
}

var app *newrelic.Application

func main() {
	// Initialize New Relic
	var err error
	app, err = newrelic.NewApplication(
		newrelic.ConfigAppName("ts-news-service"),
		newrelic.ConfigLicense(os.Getenv("NEW_RELIC_LICENSE_KEY")),
		newrelic.ConfigDistributedTracerEnabled(true),
		newrelic.ConfigLogger(newrelic.NewLogger(os.Stdout)),
	)
	if err != nil {
		log.Printf("Failed to initialize New Relic: %v", err)
		// Continue without New Relic if initialization fails
	} else {
		log.Println("New Relic agent initialized successfully")
	}

	web.Get("/(.*)", hello)
	log.Println("Starting ts-news-service on :12862")
	web.Run("0.0.0.0:12862")
}