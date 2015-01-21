(function () {

var BiblioCard = React.createClass({
    onClickCard: function (e) {
	e.preventDefault();
	this.props.handleClickCard({"alias" : this.props.alias});
    },
    render: function () {
	var alt = "Image de la carte : " + this.props.card.name,
	    img = "img?name=" + this.props.alias + "." + this.props.card.imgExt;
	return (
	    <li className="biblioCard" onClick={this.onClickCard} >
		<img src={img} title={this.props.card.name} alt={alt} />
	    </li>
	);
    }
});

var BiblioList = React.createClass({
    render: function () {
	var cardsSet = this.props.cards.cardsSet;
	var handleClickCard = this.props.handleClickCard;
	var cards = this.props.cards.cardsList.map(function (alias) {
	    var card = cardsSet[alias];
	    return (
		<BiblioCard key={card.id} alias={alias} card={card} 
                            handleClickCard={handleClickCard} />
	    );
	});
	return (
	    <ul className="biblioList" >
	        {cards}
	    </ul>
	);
    }				
});

var BiblioAdd = React.createClass({
    onCardSubmit: function (e) {
	e.preventDefault();
	
	var url = this.refs.url.getDOMNode().value.trim();
	if (! url) { return; }
	
	this.props.handleCardSubmit({url:url});
	this.refs.url.getDOMNode().value = "";
	return;
    },
    render: function () {
	return (
	    <form className="biblioAdd" onSubmit={this.onCardSubmit} >
	        <input type="text" ref="url" placeholder="URL de la carte" />
		<input type="submit" value="Ajouter" /> <br />
	    </form>
	);
    }				
});

var BiblioBox = React.createClass({
    render: function () {
	return (
	    <div className="biblioBox" >
		<h2>Bibliothèque</h2>
		<BiblioList cards={this.props.cards} 
                            handleClickCard = {this.props.handleClickCard} />
		<h3>Ajouter une carte</h3>
		<BiblioAdd handleCardSubmit={this.props.handleCardSubmit} />
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

var CardInfoBox = React.createClass({
    render: function () {
	if (this.props.alias == "") {
	    return (
	        <div className="cardInfoBox" >
		    <h2>Carte Infos</h2>
		</div>
	    );
	}
	var alt = "Image de la carte : " + this.props.card.name,
	    img = "img?name=" + this.props.alias + "." + this.props.card.imgExt;
	return (
	    <div className="cardInfoBox" >
		<h2>Carte Infos</h2>
		<img src={img} title={this.props.card.name} alt={alt} />
	    </div>
	)
    }
});

var DoroBox = React.createClass({
    loadCards: function () {
	$.ajax({
	    url: this.props.urlBiblio,
	    dataType: "json",
	    success: function (data) {
		this.setState({cards: data});
	    }.bind(this),
	    error: function (xhr, status, err) {
		console.error(this.props.urlBiblio, status, err.toString());
	    }.bind(this)
	});
    },
    handleCardSubmit: function (card) {
	$.ajax({
	    isLocal: true,
	    url: this.props.urlBiblioAdd,
	    data: card,
	    dataType: "json",
	    type: "GET",
	    success: function (data) {
		this.setState({cards: data});
	    }.bind(this),
	    error: function (xhr, status, err) {
		console.error(this.props.urlBiblioAdd, status, err.toString());
	    }.bind(this)
	});
    },
    handleClickCard: function (card) {
	if (card.alias in this.state.cards.cardsSet) {
	    this.setState({cardInfo: {
		alias: card.alias,
		card: this.state.cards.cardsSet[card.alias]
	    }});
	}
    },
    getInitialState: function () {
	return {"cards": {"cardsSet": {}, "cardsList": [], "nbcards": 0},
	        "cardInfo": {"alias": "", "card": {}}};
    },
    componentDidMount: function () {
	this.loadCards();
	setInterval(this.loadCards, this.props.pollInterval);
    },
    render: function () {
	return (
	    <div className="doroBox" >
		<BiblioBox cards = {this.state.cards}
		           handleCardSubmit = {this.handleCardSubmit}
		           handleClickCard = {this.handleClickCard} />
		<CardInfoBox alias = {this.state.cardInfo.alias}
	                     card = {this.state.cardInfo.card} />
	    </div>
	);
    }
});

var port = window.location.port,
    address = "http://127.0.0.1:" + port;

React.render(
    <DoroBox
      urlBiblio = "biblio"
      urlBiblioAdd = "biblio-add"
      pollInterval = {2000} />,
    document.getElementById("content")
);

}) ();