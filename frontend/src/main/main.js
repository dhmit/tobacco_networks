/**
 * UI Code for the visualization
 */
import React from 'react';
import PropTypes from 'prop-types';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons';

import { getCookie } from '../common'
import { create_graph, update_graph_color, update_graph_size } from './graph.js'
import './main.css';


/***************************************************************************************************
 * Controls
 * The top row of the webapp, with search bar, display controls, etc.
 **************************************************************************************************/
class Controls extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="row">
                <div className="col-6">
                    <input className="form-control"
                        type="text"
                        maxLength="20" size="20"
                        value={this.props.person_to_highlight}
                        placeholder={"Type a name here"}
                        onChange={(e) => this.props.handle_searchbar_update(e.target.value)}
                    />
                    {/*<label>Color is blue</label>*/}
                </div>
                <div className="col-1 float-right info_button">
                    <a onClick={this.props.toggle_show_table}>
                        <FontAwesomeIcon icon={faInfoCircle} />
                    </a>
                </div>
            </div>
        )
    }
}
Controls.propTypes = {
    person_to_highlight: PropTypes.string.isRequired,
    handle_searchbar_update: PropTypes.func.isRequired,
    toggle_show_table: PropTypes.func,
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
        } else if (this.props.config.viz_update_func === 'update_graph_size'){
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
            <div className="col-12 p-0 m-0" ref={this._graphRoot}>

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
        return (
            <div className="col-3">
                <div className="row float-right info_panel">
                    <button onClick={() => this.props.toggle_show_table()} type="button"
                        className="ml-2 mb-1 close" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
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

Info.propTypes ={
    mouseover: PropTypes.bool,
    currentColor: PropTypes.string,
    person: PropTypes.string,
    docs: PropTypes.number,
    words: PropTypes.number,
    show_info_panel: PropTypes.bool,
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
                person_to_highlight: "",
            },  // initial configuration for the viz
            data: null,  // data for the viz
            mouseover: false,  // info panel state (based on callbacks from viz)

            person: "",
            docs: 0,
            words: 0,
            show_info_panel: false,
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
                        this.setState({data:data});
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

    handle_searchbar_update(search_string) {
        let config = {... this.state.config};
        config.person_to_highlight = search_string;
        this.setState({config: config})

        //TODO: trigger update of visualization
    }

    submitFormHandler = event => {
        event.preventDefault();
    }

    /**
     * Calls when button is pressed.  Shows the table containing info about person when it is
     * hidden and hides table when visible.
     */
    toggle_show_table() {
        console.log('calling toggle show table!');
        this.setState({show_info_panel: !this.state.show_info_panel});
    }

    /**
     * Render the app on the page
     *
     * @returns {Node}
     */
    render() {
        if (this.state.data) {
            return (
                <div className="container-fluid">
                    <div className="row">
                        <Controls
                            person_to_highlight={this.state.config.person_to_highlight}
                            handle_searchbar_update={
                                (search_string) => this.handle_searchbar_update(search_string)
                            }
                            toggle_show_table={() => this.toggle_show_table()}
                        />
                    </div>

                    <div className="row">
                        <Viz
                            data={this.state.data}
                            config={this.state.config}
                            handle_viz_events={(event_name, data) =>
                                this.handle_viz_events(event_name, data )}
                        />
                        {this.state.show_info_panel &&
                            <Info
                                mouseover={this.state.mouseover}
                                currentColor={this.state.config.color}
                                person={this.state.person}
                                docs={this.state.docs}
                                words={this.state.words}
                                show_info_panel={this.state.show_info_panel}
                                toggle_show_table={() => this.toggle_show_table()}
                            />
                        }
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
