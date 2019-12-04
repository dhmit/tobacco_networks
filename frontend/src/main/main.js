/**
 * UI Code for the visualization
 */
import React from 'react';
import PropTypes from 'prop-types';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons';

import { getCookie } from '../common'
import * as d3 from 'd3';
import { create_graph, update_graph} from './graph.js'
import './main.css';


/***************************************************************************************************
 * Controls
 * The top row of the webapp, with search bar, display controls, etc.
 **************************************************************************************************/
class Controls extends React.Component {
    constructor(props) {
        super(props);
    }

    validate_input_and_maybe_search() {
        // Check if the person we're searching for actually exists
        const search_string = this.props.searchbar_value;
        this.props.update_searchbar_value(search_string);

        const nodes = this.props.nodes;
        let is_name = false;
        for (const node of nodes) {
            const name = node.name;
            if (search_string.toLowerCase() === name.toLowerCase()) {
                is_name = true;
                this.props.handle_searchbar_query(search_string, true);
                break;
            } else {
                // TODO: tell the user the name isn't in the list

            }
        }
        if (is_name === false) {
            this.props.handle_searchbar_query(search_string, false);
        }
    }

    render() {
        return (
            <div className="row">
                <div className="col-4">
                    <input className="form-control"
                        type="text"
                        maxLength="20" size="20"
                        value={this.props.searchbar_value}
                        onChange={(e) => this.props.update_searchbar_value(e.target.value)}
                        placeholder={"Type a name here"}
                    />
                </div>
                <div className="col-6">
                    <div className="form-check float-right">
                        <input type="checkbox" className="form-check-input"
                            onChange={this.props.toggle_checkbox}/>
                        <label>Check to cluster</label>
                    </div>
                    <div id="info_button">
                        <a onClick={this.props.toggle_show_table}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                        </a>
                    </div>
                    <button
                        className="button"
                        onClick={() => this.validate_input_and_maybe_search()}
                    >Search</button>
                    <button
                        className="button"
                        onClick={() => {
                            this.props.update_searchbar_value("");
                            this.props.handle_searchbar_query("", false);
                        }}
                    >Clear</button>
                </div>
                <div className="col-4">
                    <div className="form-group">
                        <label htmlFor="exampleFormControlSelect1">Dataset</label>
                        <select className="form-control"
                            value={this.props.dataset_name}
                            onChange={(e) => this.props.update_dataset(e.target.value)}
                        >
                            <option value="lawyers">Lawyers</option>
                            <option value="research_directors">Research Directors</option>
                            <option value="sterling">Theodore Sterling</option>
                            <option value="top_100_edges">100 Strongest Edges</option>
                            <option value="test">Test Dataset</option>
                        </select>
                    </div>
                </div>
            </div>
        );
    }
}


Controls.propTypes = {
    toggle_checkbox: PropTypes.func,
    toggle_show_table: PropTypes.func,
    searchbar_value: PropTypes.string.isRequired,
    update_searchbar_value: PropTypes.func.isRequired,
    handle_searchbar_query: PropTypes.func.isRequired,
    nodes: PropTypes.array.isRequired,
    dataset_name: PropTypes.string.isRequired,
    update_dataset: PropTypes.func.isRequired
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
        window.d3 = d3;
    }

    componentDidUpdate() {
        // D3 Code to update the chart
        if (this.props.config.viz_update_func === undefined) {
            return;
        }

        let update_func, action;
        if (this.props.config.viz_update_func === 'cluster_nodes') {
            update_func = update_graph;
            action = 'cluster_nodes';
        }
        else if (this.props.config.viz_update_func === 'focus_node') {
            update_func = update_graph;
            action = 'focus';
        }
        else if (this.props.config.viz_update_func === 'unfocus_node') {
            update_func = update_graph;
            action = 'unfocus';
        }
        else if (this.props.config.viz_update_func === 'create_graph') {
            document.getElementById('graph_root').innerHTML = '';
            update_func = create_graph;
        }


        update_func(
            this._graphRoot.current,
            this.props.data,
            this.props.config,
            action,
        );
    }

    render() {
        return (
            <div className="col-12 p-0 m-0" ref={this._graphRoot} id='graph_root'>

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
            <div id="info_panel">
                <button onClick={this.props.toggle_show_table} type="button"
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
                        <tr>
                            <th scope="row">Affiliation</th>
                            <td>{this.props.affiliation.length > 0 ? this.props.affiliation :
                                ""}</td>
                        </tr>
                    </tbody>
                </table>
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
    affiliation: PropTypes.string,
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
                searchbar_value: "",
                dataset_name: 'test'
            },  // initial configuration for the viz
            data: null,  // data for the viz
            mouseover: false,  // info panel state (based on callbacks from viz)
            clicked:["false", null],
            person: "",
            docs: 0,
            words: 0,
            affiliation: "",
            show_info_panel: false,
            cluster_nodes: true,
        };
        this.csrftoken = getCookie('csrftoken');
    }
    /**
     * Runs when the MainView item is connected to the DOM.
     */
    componentDidMount() {
        this.load_dataset(this.state.config.dataset_name);
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
            if (this.state.clicked[0] == "false"){
                this.setState({clicked: [!(this.state.clicked), data.name]})
            }
            else if (this.state.clicked[0] == "true"){
                if (data.name == this.state.clicked[1]){
                    this.setState({clicked: [!(this.state.clicked), data.name]})
                }
            }
            this.setState({person: data.name});
            this.setState({docs: data.docs});
            this.setState({words: data.words});
            this.setState({affiliation: data.affiliation});
            if (this.state.show_info_panel === false) {
                this.setState({show_info_panel: true});
            }
        }
    }

    toggle_checkbox() {
        this.setState({cluster_nodes: !this.state.cluster_nodes});
        const config = {... this.state.config};
        config.cluster_nodes = this.state.cluster_nodes;
        config.viz_update_func = 'cluster_nodes';
        this.setState({config: config});

    }

    /**
     * Handles search bar update
     *
     * @param event_name: String
     */
    handle_searchbar_query(search_string, action) {
        const config = {... this.state.config};
        config.search_person_name = search_string;
        if (action === true) {
            config.viz_update_func = 'focus_node';
        } else {
            config.viz_update_func = 'unfocus_node';
        }
        config.searchbar_value = search_string;
        this.setState({config: config});

    }

    update_searchbar_value(search_string) {
        const config = {...this.state.config};
        config.searchbar_value = search_string;
        this.setState({config: config});
    }

    submitFormHandler = event => {
        event.preventDefault();
    }

    update_dataset(dataset_name) {
        console.log(dataset_name);
        const config = {...this.state.config};
        config.dataset_name = dataset_name;
        config.viz_update_func = 'create_graph';
        this.load_dataset(config.dataset_name);
        this.setState({config: config});
    }

    async load_dataset(dataset_name) {
        const dataset = encodeURIComponent(dataset_name);
        fetch(`get_network_data?dataset=${dataset}`)
            .then((response) => {
                response
                    .json()
                    .then((data) => {
                        console.log("new data", data);
                        this.setState({data:data});
                    })
            }).catch(() => {
                console.log("error");
            });
    }


    /**
     * Calls when button is pressed.  Shows the table containing info about person when it is
     * hidden and hides table when visible.
     */
    toggle_show_table() {
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
                    <Controls  // this is its own row
                        person_to_highlight={this.state.config.person_to_highlight}
                        handle_searchbar_query={
                            (search_string, action) => this.handle_searchbar_query(search_string,
                                action)
                        }
                        update_searchbar_value={
                            (search_string) => this.update_searchbar_value(search_string)
                        }
                        toggle_checkbox={() => this.toggle_checkbox()}
                        toggle_show_table={() => this.toggle_show_table()}
                        cluster_nodes={this.state.cluster_nodes}
                        nodes={this.state.data.nodes}
                        searchbar_value={this.state.config.searchbar_value}
                        dataset_name={this.state.config.dataset_name}
                        update_dataset={
                            (dataset_name) => this.update_dataset(dataset_name)
                        }
                    />

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
                                affiliation={this.state.affiliation}
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
