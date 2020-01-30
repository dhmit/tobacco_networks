
import React from 'react';
//import PropTypes from 'prop-types';
import MainView from "./main";
import PropTypes from "prop-types";

import './tufte.css'


export class EssayView extends React.Component {
    constructor(props){
        super(props);
    }


    render(){

        let epigraph = null;
        if (this.props.epigraph){
            epigraph =
                <div className="epigraph">
                    <blockquote>
                        <p>{this.props.epigraph.content}</p>
                        <footer>{this.props.epigraph.author}</footer>
                    </blockquote>
                </div>;
        }

        let subtitle = null;
        if (this.props.subtitle){
            subtitle = <h6>{this.props.subtitle}</h6>
        }
        const essay_header =
            <>
                <h1>{this.props.title}</h1>
                {subtitle}
                <p className="subtitle">{this.props.authors}</p>
                {epigraph}
                <section>
                    {this.props.introduction}
                </section>
            </>;



        return(
            <>
                <div className='row'>
                    <div className='col-12'>
                        <div className='tufte-body' id="essay_body">
                            <article>
                                {essay_header}
                                <MainView
                                    dataset_name={this.props.dataset_name}
                                    show_dataset_selector={false}
                                    element_for_graph_sizing='essay_body'
                                />
                                {this.props.essay_content}
                            </article>
                        </div>
                    </div>
                </div>
            </>
        )
    }
}
EssayView.propTypes ={
    title: PropTypes.string.isRequired,
    subtitle: PropTypes.string,
    epigraph: PropTypes.object,
    authors: PropTypes.string.isRequired,
    introduction: PropTypes.node.isRequired,
    essay_content: PropTypes.node.isRequired,
    dataset_name: PropTypes.string.isRequired
};


export class EssaySideNote extends React.Component {

    render(){
        let sidenote_content;
        if (this.props.url){
            sidenote_content =
                <span className="sidenote">
                    <a href={this.props.url}>{this.props.content}</a>
                </span>;
        } else {
            sidenote_content = <span className="sidenote">{this.props.content}</span>;
        }
        return(
            <>
                <label htmlFor="sn-extensive-use-of-sidenotes"
                    className="margin-toggle sidenote-number"></label>&nbsp;
                <input type="checkbox" id="sn-extensive-use-of-sidenotes"
                    className="margin-toggle"/>
                {sidenote_content}
            </>
        )
    }
}
EssaySideNote.propTypes = {
    content: PropTypes.string.isRequired,
    url: PropTypes.string
};

