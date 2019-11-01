/**
 * UI Code for the visualization
 */
import React from 'react';
import PropTypes from 'prop-types';

import { getCookie } from '../common'
import { create_graph, update_graph_color, update_graph_size } from './graph.js'
import './main.css';


/***************************************************************************************************
 * Controls and settings components for the visualization
 **************************************************************************************************/
class Controls extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const checked = this.props.config.color === 'blue';
        return (
            <div className="col-3">
                <input
                    type="checkbox"
                    checked={checked}
                    onChange={this.props.handle_checkbox}
                />
                {/*<label>Color is blue</label>*/}
            </div>
        );

    }
}

Controls.propTypes = {
    config: PropTypes.object.isRequired,
    handle_checkbox: PropTypes.func.isRequired,
};


/***************************************************************************************************
 * Wrapper for the Visualization
 **************************************************************************************************/
class Viz extends React.Component {
    constructor(props) {
        super(props);
        this._graphRoot = React.createRef();
    }

    componentDidMount() {
        // D3 Code to create the chart
        create_graph(
            this._graphRoot.current,  // current gives the DOM object (as opposed to the React ref)
            this.props.data,
            this.props.config,
            this.props.handle_viz_events,
        );
    }

    componentDidUpdate() {
        // D3 Code to update the chart

        if (this.props.config.viz_update_func === undefined) {
            return;
        }

        let update_func;
        if (this.props.config.viz_update_func === 'update_graph_color') {
            update_func = update_graph_color;
        }
        else if (this.props.config.viz_update_func === 'update_graph_size'){
            update_func = update_graph_size;
        }
        update_func(
            this._graphRoot.current,
            this.props.data,
            this.props.config,
        );
    }

    render() {
        return (
            <div className="col-9" ref={this._graphRoot}>

            </div>
        )
    }
}
// data: PropTypes.arrayOf(PropTypes.object).isRequired,

Viz.propTypes = {
    data: PropTypes.objectOf(PropTypes.array).isRequired,
    config: PropTypes.object.isRequired,
    handle_viz_events: PropTypes.func,
};

/**
 * Info panel - data from the visualization
 */
class Info extends React.Component {
    constructor(props) {
        super(props);
    }



    render() {
        if (!this.props.showTableData) {
            return (
                <div onClick={() => this.props.toggle_show_table()} className="row float-right" id="toggle">
                    <a className="row" href="#toggleDisplayButton" data-toggle="collapse">
                        <img id="info_button" src="https://cdn1.iconfinder.com/data/icons/education-set-4/512/information-512.png"/>
                    </a>
                </div>
            );
        } else {
            return (
                <div className="col-3">
                    <div className="collapse row float-right" id="toggleDisplayButton">
                        <table className="table">
                            <tbody>
                                <tr>
                                    <th scope="row">Name:</th>
                                    <td>{this.props.person.length > 0 ? this.props.person : ""}</td>
                                </tr>
                                <tr>
                                    <th scope="row">Docs</th>
                                    <td>{this.props.docs > 0 ? this.props.docs : 0}</td>
                                </tr>
                                <tr>
                                    <th scope="row">Words</th>
                                    <td>{this.props.words > 0 ? this.props.words : 0}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            );
        }
    }
}

Info.propTypes ={
    mouseover: PropTypes.bool,
    currentColor: PropTypes.string,
    person: PropTypes.string,
    docs: PropTypes.number,
    words: PropTypes.number,
    showTableData: PropTypes.bool,
    toggle_show_table: PropTypes.func,
};


/***************************************************************************************************
 * Main component for the main view.
 **************************************************************************************************/
class MainView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            config: {
                width: window.innerWidth,
                height: window.innerHeight,
                color: 'blue',
            },  // initial configuration for the viz
            data: null,  // data for the viz
            mouseover: false,  // info panel state (based on callbacks from viz)
            person: "",
            docs: 0,
            words: 0,
            showTableData: false,
        };
        this.csrftoken = getCookie('csrftoken');
    }

    /**
     * Runs when the MainView item is connected to the DOM.
     */
    componentDidMount() {
        fetch("get_network_data")
            .then((response) => {
                response
                    .json()
                    .then((data) => {
                        this.setState({data});
                    })
            }).catch(() => {
                console.log("error");
            });
        window.addEventListener("resize", () => {
            const config = {...this.state.config};
            config.width = window.innerWidth;
            config.height = window.innerHeight;

            config.viz_update_func = 'update_graph_size';
            this.setState({
                config: config,
            })
        });
    }

    /**
     * Calls when checkbox is changed.  Changes the color from blue to red or vice versa.
     */
    handle_checkbox() {
        // "..." is the 'spread' operator - this is a copy
        const config = {...this.state.config};
        if (config.color === 'blue') {
            config.color = 'red';
        } else {
            config.color = 'blue'
        }
        //TODO: rewrite this to update width and height for the vis
        config.viz_update_func = 'update_graph_color';
        this.setState({
            config: config,
        })
    }

    /**
     * Handles a visualization event
     *
     * @param event_name: String
     * @param data: Object
     */
    handle_viz_events(event_name, data) { // eslint-disable-line no-unused-vars
        if (event_name === "mouseover") {
            this.setState({mouseover: true});
        } else if (event_name === "mouseout") {
            this.setState({mouseover: false});
        } else if (event_name === "click") {
            this.setState({person: data.name});
            this.setState({docs: data.docs});
            this.setState({words: data.words});
        }
    }

    /**
     * Calls when button is pressed.  Shows the table containing info about person when it is
     * hidden and hides table when visible.
     */
    toggle_show_table() {
        console.log(this.state.showTableData)
        this.setState({
            showTableData: !this.state.showTableData
        })
        console.log(this.state.showTableData)
    }

    /**
     * Render the app on the page
     *
     * @returns {Node}
     */
    render() {
        if (this.state.data) {
            return (
                <div className="container">
                    <div className="row">
                        <Controls
                            handle_checkbox={() => this.handle_checkbox()}
                            config={this.state.config}
                        />
                    </div>

                    <div className="row">
                        <Viz
                            data={this.state.data}
                            config={this.state.config}
                            handle_viz_events={(event_name, data) =>
                                this.handle_viz_events(event_name, data )}
                        />
                        <Info
                            mouseover={this.state.mouseover}
                            currentColor={this.state.config.color}
                            person={this.state.person}
                            docs={this.state.docs}
                            words={this.state.words}
                            showTableData={this.state.showTableData}
                            toggle_show_table={() => this.toggle_show_table()}
                        />
                    </div>
                </div>
            );
        } else {
            return (
                <div>Loading!</div>
            )
        }
    }
}

// when importing Main what do we get?
export default MainView;
