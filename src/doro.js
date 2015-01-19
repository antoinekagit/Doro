var BiblioCard = React.createClass({
    render: function () {
	var alt = "aperçu de : " + this.props.name;
	return (
	    <li className="biblioCard" >
		<img src={this.props.img} title={this.props.name} alt={this.alt} />
	    </li>
	);
    }
});

var BiblioList = React.createClass({
    render: function () {
	var cards = this.props.data.cards.map(function (c) {
	    return (
		<BiblioCard key={c.id} id={c.id} name={c.name} img={c.img} />
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
    handleSubmit: function (e) {
	e.preventDefault();
	
	var url = this.refs.url.getDOMNode().value.trim();
	if (! url) { return; }
	
	this.props.onCardSubmit({url:url});
	this.refs.url.getDOMNode().value = "";
	return;
    },
    render: function () {
	return (
	    <form className="biblioAdd" onSubmit={this.handleSubmit} >
	        <input type="text" ref="url" placeholder="URL de la carte" />
		<input type="submit" value="Ajouter" /> <br />
	    </form>
	);
    }				
});

var BiblioBox = React.createClass({
    loadCards: function () {
	$.ajax({
	    url: this.props.urlBiblio,
	    dataType: "json",
	    success: function (data) {
		this.setState({data: data});
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
	    dataType: "json",
	    type: "GET",
	    data: card,
	    success: function (data) {
		console.log(data);
		this.setState({data: data});
	    }.bind(this),
	    error: function (xhr, status, err) {
		console.error(this.props.urlBiblioAdd, status, err.toString());
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
	    <div className="biblioBox" >
		<BiblioList data={this.state.data} />
		<h3>Ajouter une carte</h3>
		<BiblioAdd onCardSubmit={this.handleCardSubmit} />
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
    <BiblioBox 
      urlBiblio="http://127.0.0.1:8001/biblio"
      urlBiblioAdd="http://127.0.0.1:8001/biblio-add"
      pollInterval={2000} />,
    document.getElementById("biblio")
);
