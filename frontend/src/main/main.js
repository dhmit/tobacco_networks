/**
 * UI Code for the visualization
 */
import React from 'react';
import PropTypes from 'prop-types';

import { getCookie } from '../common'
import { create_graph, update_graph_color } from './graph.js'
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
                <label>Color is blue</label>
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
        if (this.props.config.viz_update_func === 'update_graph_color') {
            update_graph_color(
                this._graphRoot.current,
                this.props.data,
                this.props.config,
            );
        }
    }

    render() {
        return (
            <div className="col-6" ref={this._graphRoot}>

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

    /**
     * Calls when button is pressed.  Shows the table containing info about person when it is
     * hidden and hides table when visible.
     */
    toggle_show_table(tb) {
        this.setState({
            showTableData:!tb
        })
    }

    render() {
        return (
            <div className="col-3">
                <p>Your mouse is {this.props.mouseover ? 'OVER' : 'NOT OVER'}  a bar on the viz!</p>
                <p>The current viz color is {this.props.currentColor}</p>
                <table className="table">
                    <tbody><tr>
                        <th scope="row">Name:</th>
                        <td>{this.props.person.length > 0 ? this.props.person : ""}</td>
                    </tr>
                    <tr>
                        <th scope="row">Docs</th>
                        <td></td>
                    </tr>
                    <tr>
                        <th scope="row">Words</th>
                        <td></td>
                    </tr>
                    </tbody>
                </table>
                <button onClick={()=>this.toggle_show_table()}>Toggle Display</button>
            </div>
        );
    }
}
Info.propTypes ={
    mouseover: PropTypes.bool,
    currentColor: PropTypes.string,
    person: PropTypes.string,
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
                width: 1000,
                height: 800,
                color: 'blue',
            },  // initial configuration for the viz
            data: null,  // data for the viz
            mouseover: false,  // info panel state (based on callbacks from viz)
            person: "",
            showTableData: true,
        };
        this.csrftoken = getCookie('csrftoken');
    }

    /**
     * Runs when the MainView item is connected to the server.
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
        }
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
                            showTableData={this.state.showTableData}
                            toggle_show_data={(showTableData) => this.toggle_show_table(showTableData)}
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
