/*
{
    "id": 2,
    "cards": 
[
{"id": 0,
"name": "Lucky Chance", 
"img": "http://img3.wikia.nocookie.net/__cb20120720012414/yugioh/images/thumb/4/4f/LuckyChance-LODT-EN-C-UE.png/300px-LuckyChance-LODT-EN-C-UE.png"}
]
}
*/

var DeckCard = React.createClass({
    render: function () {
	var alt = "aperçu de : " + this.props.name;
	return (
	    <li className="deckCard" >
		<img src={this.props.img} title={this.props.name} alt={this.alt} />
	    </li>
	);
    }
});

var DeckList = React.createClass({
    render: function () {
	var cards = this.props.data.cards.map(function (c) {
	    return (
		<DeckCard key={c.id} id={c.id} name={c.name} img={c.img} />
	    );
	});
	return (
	    <ul className="deckList" >
	        {cards}
	    </ul>
	);
    }				
});

var AjouterCarte = React.createClass({
    handleSubmit: function (e) {
	e.preventDefault();
	
	var url = this.refs.url.getDOMNode().value.trim();
	if (! url) { return; }
	
	this.props.onCardSubmit({id: 2, name:"lol", img:"LOL"});
	this.refs.url.getDOMNode().value = "";
	return;
    },
    render: function () {
	return (
	    <form className="ajouterCarte" onSubmit={this.handleSubmit} >
	        <input type="text" ref="url" placeholder="URL de la carte" />
		<input type="submit" value="Ajouter" /> <br />
	    </form>
	);
    }				
});

var DeckBox = React.createClass({
    loadCards: function () {
	$.ajax({
	    url: this.props.urlCards,
	    dataType: "json",
	    success: function (data) {
		this.setState({data: data});
	    }.bind(this),
	    error: function (xhr, status, err) {
		console.error(this.props.urlCards, status, err.toString());
	    }.bind(this)
	});
    },
    handleCardSubmit: function (card) {
	$.ajax({
	    isLocal: true,
	    url: this.props.urlCardsAdd,
	    dataType: "json",
	    type: "GET",
	    data: card,
	    success: function (data) {
		console.log(data);
		this.setState({data: data});
	    }.bind(this),
	    error: function (xhr, status, err) {
		console.error(this.props.urlCardsAdd, status, err.toString());
	    }.bind(this)
	});
    },
    getInitialState: function () {
	return {data: {id: 0, cards: [], decks: []}}
    },
    componentDidMount: function () {
	this.loadCards();
	setInterval(this.loadCards, this.props.pollInterval);
    },
    render: function () {
	return (
	    <div className="deckBox" >
		<DeckList data={this.state.data} />
		<h3>Ajouter une carte</h3>
		<AjouterCarte onCardSubmit={this.handleCardSubmit} />
		<p>
		<strong>Aide : </strong> <br />
		<span>Il faut utiliser les URL du site </span>
	        <a href="http://yugioh.wikia.com" >yugioh.wikia.com</a> 
		<span>.</span> <br /> 
                <span>par exemple "<a href="http://yugioh.wikia.com/wiki/Lucky_Chance" >http://yugioh.wikia.com/wiki/Lucky_Chance</a>".</span>
		</p>
	    </div>
	);
    }
});

React.render(
    <DeckBox 
      urlCards="http://127.0.0.1:8001/cards"
      urlCardsAdd="http://127.0.0.1:8001/cards-add"
      pollInterval={2000} />,
    document.getElementById("content")
);

console.log("react");