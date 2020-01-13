/**
 * UI Code for the visualization
 */
import React from 'react';
import PropTypes from 'prop-types';

import { Autocomplete } from '@material-ui/lab';
import { TextField } from '@material-ui/core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons';

import { getCookie } from '../common'
import * as d3 from 'd3';
import { create_graph, update_graph} from './graph.js'
import {update_node_degree_and_visibility} from "./node_degree_calculation";
import './main.css';

/***************************************************************************************************
 * Controls
 * The top row of the webapp, with search bar, display controls, etc.
 **************************************************************************************************/
class Controls extends React.Component {
    constructor(props) {
        super(props);
    }

    validate_searchbar_input_and_maybe_search(search_string) {
        // Check if the person we're searching for actually exists
        console.log("Searching: " + search_string);
        const nodes = this.props.nodes;
        for (const node of nodes) {
            const name = node.name;

            if (search_string.toLowerCase() === name.toLowerCase()) {
                this.props.handle_searchbar_search(name);
                return;
            }
        }
    }

    autocomplete_change(value, reason) {
        console.log(value + ": In the change function because of: " + reason);
        if (reason === "clear") {
            this.props.handle_searchbar_clear();
        } else {
            this.validate_searchbar_input_and_maybe_search(value);
            this.props.update_searchbar_value(value);
        }
    }

    render() {
        return (
            <div className="row">
                <div className="col-4">
                    <Autocomplete
                        id="free-solo-demo"
                        freeSolo={true}
                        options={this.props.data_names.map(option => option.name)}
                        renderInput={params => (
                            <TextField {...params}
                                placeholder="Type a name here"
                                //maxLength="20" size="20"
                                margin="normal"
                                variant="outlined" fullWidth
                                value={this.props.searchbar_value}
                                onChange={(e) => this.props.update_searchbar_value(e.target.value)}
                            />
                            //TODO Clear X trtigger clear function; search when automcomplete
                        )}
                        autoComplete={true}
                        forcePopupIcon={false}
                        onChange={(_event, value) => this.props.update_searchbar_value(value)}
                        onInputChange={(_event, value, reason) =>
                            this.autocomplete_change(value, reason)}
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
                        onClick={() =>
                            // eslint-disable-next-line max-len
                            this.validate_searchbar_input_and_maybe_search(this.props.searchbar_value)}
                    >Search
                    </button>

                    <button
                        className="button"
                        onClick={() => {
                            this.props.handle_searchbar_clear();
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
    searchbar_value: PropTypes.string.isRequired,
    toggle_checkbox: PropTypes.func,
    toggle_show_table: PropTypes.func,
    handle_searchbar_query: PropTypes.func.isRequired,
    handle_searchbar_search: PropTypes.func.isRequired,
    handle_searchbar_clear: PropTypes.func.isRequired,
    update_searchbar_value: PropTypes.func.isRequired,
    nodes: PropTypes.array.isRequired,
    dataset_name: PropTypes.string.isRequired,
    update_dataset: PropTypes.func.isRequired,
    data_names: PropTypes.array
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

        if (this.props.config.viz_update_func === 'create_graph') {
            document.getElementById('graph_root').innerHTML = '';
            create_graph(this._graphRoot.current, this.props.data, this.props.config,
                this.props.handle_viz_events);
            return
        }

        let update_func, action;
        if (this.props.config.viz_update_func === 'cluster_nodes') {
            update_func = update_graph;
            action = 'cluster_nodes';
        }
        else if (this.props.config.viz_update_func === 'update_focus') {
            update_func = update_graph;
            action = 'update_focus';
        }

        update_func(
            {... this._graphRoot.current},
            {... this.props.data},
            {... this.props.config},
            {... this.props.data_bindings},
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
    data_bindings: PropTypes.object.isRequired,
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
                height: window.innerHeight - 100,
                person_to_highlight: "",
                dataset_name: 'test',
                cluster_nodes: true,
                selection_active: false,
                selection_name: undefined,
                mouseover_active: false,
                show_info_panel: false,
                searchbar_value: "",
                selected_viz_degree: 2
            },  // initial configuration for the viz
            data: null,  // data for the viz
            data_bindings: {}, // data bindings for d3
            mouseover: false,  // info panel state (based on callbacks from viz)

            person: "",
            docs: 0,
            words: 0,
            affiliation: "",
            //show_info_panel: false,
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


        if (event_name === 'update_data_bindings'){
            if (!data === null) {
                console.log(data.clusters === this.state.data_bindings.clusters);
            }
            this.setState({data_bindings: data});
            return
        }

        // all other viz events use the data from a node -> rename
        let config = {... this.state.config};
        let node = data;
        if (event_name === "mouseover") {
            // if a selection is already active, don't change to mouseover target
            if (!config.selection_active){
                config.viz_update_func = 'update_focus';
                const data = update_node_degree_and_visibility(
                    {... this.state.data}, {... this.state.config}, node.name);
                this.setState({data: data, config: config});
            }

        } else if (event_name === "mouseout") {
            if (!config.selection_active){
                config.viz_update_func = 'update_focus';
                const data = update_node_degree_and_visibility(
                    {... this.state.data}, {... this.state.config});
                this.setState({data: data, config: config});
            }
        } else if (event_name === "click") {
            let data;

            // select new person
            if (!config.selection_active || node.name !== this.state.config.selection_name){

                // update center names to selected node
                data = {... this.state.data};
                // turning the next two lines into a one-liner gives an error. unclear why.
                data.center_names = {};
                data.center_names[node.name] = true;
                this.setState({data: data});

                config.selection_active = true;
                config.selection_name = node.name;
                config.show_info_panel = true;
                config.searchbar_value = node.name;
                data = update_node_degree_and_visibility(
                    {... this.state.data}, {... this.state.config}, node.name);
            } else {

                data = {... this.state.data};
                data.center_names = data.center_names_backup;
                this.setState({data: data});

                config.selection_active = false;
                config.selection_name = undefined;
                config.show_info_panel = false;
                data = update_node_degree_and_visibility(
                    {... this.state.data}, {... this.state.config});
            }
            this.setState({data: data, config: config});
        }
    }

    toggle_checkbox() {
        // this.setState({cluster_nodes: !this.state.config.cluster_nodes});
        let config = {... this.state.config};
        config.cluster_nodes = !this.state.config.cluster_nodes;
        config.viz_update_func = 'cluster_nodes';
        this.setState({config: config});
    }

    /**
     * Searches the graph for the person's name
     * @param search_string String containing the name to search for
     */
    handle_searchbar_search(search_string) {
        let config = {... this.state.config};
        config.searchbar_value = search_string;
        config.viz_update_func = 'update_focus';
        config.selection_active = true;
        config.selection_name = search_string;
        config.show_info_panel = true;
        const data = update_node_degree_and_visibility(
            {... this.state.data}, {... this.state.config}, search_string);
        this.setState({data: data, config: config});
        console.log("Searched")
    }

    /**
     * Clears the searchbar
     * TODO: Make the clear actually clear the text of the searchbar, propbably will be done in
     * Content
     */
    handle_searchbar_clear() {
        let config = {... this.state.config};
        config.searchbar_value = "";
        config.selection_active = false;
        config.selection_name = undefined;
        const data = update_node_degree_and_visibility(
            {... this.state.data}, {... this.state.config});
        this.setState({data: data, config: config});
        console.log("Cleared")
    }

    update_searchbar_value(search_string) {
        const config = {...this.state.config};
        config.searchbar_value = search_string;
        this.setState({config: config});
        console.log(this.state.config.searchbar_value)
    }

    submitFormHandler = event => {
        event.preventDefault();
    };

    update_dataset(dataset_name) {
        this.setState({data: null});
        let config = {...this.state.config};
        config.dataset_name = dataset_name;
        config.viz_update_func = 'create_graph';
        this.setState({config: config});
        this.load_dataset(config.dataset_name);

        //setting update to undefined after loading to prevent infinite loop of
        // update -> setting data bindings -> update
        config = {... this.state.config};
        config.viz_update_func = undefined;
        this.setState({config: config})
    }

    async load_dataset(dataset_name) {
        const dataset = encodeURIComponent(dataset_name);
        fetch(`get_network_data?dataset=${dataset}`)
            .then((response) => {
                response
                    .json()
                    .then((data) => {
                        console.log("new data", data);
                        // create a copy of the center names so we can restore them on unfocus.
                        data.center_names_backup = {... data.center_names};
                        this.setState({data:data});
                        return true
                    })
            }).catch(() => {
                console.log("error");
                return false
            });

    }


    /**
     * Calls when button is pressed.  Shows the table containing info about person when it is
     * hidden and hides table when visible.
     */
    toggle_show_table() {
        let config = {...this.state.config};
        config.show_info_panel = !config.show_info_panel;
        this.setState({config: config});
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
                        handle_searchbar_search={(search_string) =>
                            this.handle_searchbar_search(search_string)}
                        handle_searchbar_clear={() => this.handle_searchbar_clear()}
                        update_searchbar_value={(e) => this.update_searchbar_value(e)}
                        toggle_checkbox={() => this.toggle_checkbox()}
                        toggle_show_table={() => this.toggle_show_table()}
                        cluster_nodes={this.state.config.cluster_nodes}
                        nodes={this.state.data.nodes}
                        searchbar_value={this.state.config.searchbar_value}
                        dataset_name={this.state.config.dataset_name}
                        update_dataset={
                            (dataset_name) => this.update_dataset(dataset_name)
                        }
                        data_names={this.state.data.nodes}

                    />

                    <div className="row">
                        <Viz
                            key={this.state.config.dataset_name}
                            data={this.state.data}
                            config={this.state.config}
                            data_bindings={this.state.data_bindings}
                            handle_viz_events={(event_name, data) =>
                                this.handle_viz_events(event_name, data )}
                        />
                        {this.state.config.show_info_panel &&
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
