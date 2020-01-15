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
        const nodes = this.props.nodes;
        for (const node of nodes) {
            const name = node.name;

            if (search_string.toLowerCase() === name.toLowerCase()) {
                this.props.handle_searchbar_search_and_focus_grpah(name);
                return;
            }
        }
    }

    autocomplete_change(value, reason) {
        if (reason === "clear") {
            this.props.handle_searchbar_clear_and_unfocus_graph();
        } else {

            if (value !== null) {
                this.validate_searchbar_input_and_maybe_search(value);
                this.props.update_searchbar_value(value);
            } else {
                this.validate_searchbar_input_and_maybe_search("");
                this.props.update_searchbar_value("");
            }
        }
    }

    render() {

        let dataset_selector = null;
        if (this.props.show_dataset_selector){
            dataset_selector =
                <div id="middle_controls" className="col-4">
                    <div className="form-group">
                        <select className="form-control float-left"
                            value={this.props.dataset_name}
                            onChange={(e) => this.props.update_dataset(e.target.value)}
                        >
                            <option value="lawyers">Lawyers</option>
                            <option value="research_directors">Research Directors</option>
                            <option value="sterling">Theodore Sterling</option>
                        </select>
                    </div>
                </div>;
        }

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
                        )}
                        inputValue = {this.props.searchbar_value}
                        autoComplete={true}
                        forcePopupIcon={false}
                        onChange={(_event, value) => this.props.update_searchbar_value(value)}
                        onInputChange={(_event, value, reason) =>
                            this.autocomplete_change(value, reason)}
                    />
                </div>

                {dataset_selector}

                <div className="col-4">
                    <div id="info_button">
                        <a onClick={this.props.toggle_show_table}>
                            <FontAwesomeIcon icon={faInfoCircle} />
                        </a>
                    </div>
                </div>
            </div>
        );
    }
}


Controls.propTypes = {
    searchbar_value: PropTypes.string.isRequired,
    toggle_show_table: PropTypes.func,
    handle_searchbar_search_and_focus_grpah: PropTypes.func.isRequired,
    handle_searchbar_clear_and_unfocus_graph: PropTypes.func.isRequired,
    update_searchbar_value: PropTypes.func.isRequired,
    handle_viz_events: PropTypes.func.isRequired,
    nodes: PropTypes.array.isRequired,
    dataset_name: PropTypes.string.isRequired,
    update_dataset: PropTypes.func.isRequired,
    data_names: PropTypes.array,
    show_dataset_selector: PropTypes.bool
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

Viz.propTypes = {
    data: PropTypes.object.isRequired,
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
                            <td>{this.props.person.name.length > 0 ?
                                this.props.person.name : ""}</td>
                        </tr>
                        <tr>
                            <th scope="row">Docs</th>
                            <td>{this.props.person.docs > 0 ? this.props.person.docs : 0}</td>
                        </tr>
                        <tr>
                            <th scope="row">Affiliation</th>
                            <td>{this.props.person.affiliation.length > 0 ?
                                this.props.person.affiliation : ""}</td>
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
    person: PropTypes.object,
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
                // width: window.innerWidth,
                // height: window.innerHeight - 100,
                // width: 1000,
                // height: 600,
                element_for_graph_sizing: this.props.element_for_graph_sizing,
                person_to_highlight: "",
                dataset_name: this.props.dataset_name,
                cluster_nodes: true,
                selection_active: false,
                selection_name: undefined,
                mouseover_active: false,
                show_info_panel: false,
                searchbar_value: "",
                selected_viz_degree: 2,
                person_to_display_info: {name: "", affiliation: "", docs: 0},
                show_dataset_selector: this.props.show_dataset_selector
            },  // initial configuration for the viz
            data: null,  // data for the viz
            data_bindings: {}, // data bindings for d3
            mouseover: false,  // info panel state (based on callbacks from viz)

        };
        this.csrftoken = getCookie('csrftoken');

    }

    /**
     * Runs when the MainView item is connected to the DOM.
     */
    componentDidMount() {
        // let config = {... this.state.config};
        // let dataset_name = this.state.config.dataset_name;
        // if (this.props.dataset_name) {
        //     config.dataset_name = this.props.dataset_name;
        //     dataset_name = this.props.dataset_name;
        // }
        // if (this.props.show_dataset_selector){
        //     config.show_dataset_selector = this.props.show_dataset_selector;
        // }

        let config = {... this.state.config};
        if (!this.props.dataset_name){
            config.dataset_name = 'research_directors';
        }
        if (this.props.show_dataset_selector===null){
            config.show_dataset_selector = true;
        }
        this.setState({config}, () => {
            this.load_dataset(this.state.config.dataset_name);
        });
    }

    /**
     * Gets the data of the person that we are searching for
     * @param person_to_focus The name of the person to look for
     * @returns an object that contains the required data to display
     */
    get_person_data(person_to_focus) {
        const people = this.state.data.nodes;
        for (let i = 0; i < people.length; i++) {
            if (people[i].name === person_to_focus) {
                return people[i];
            }
        }
    }


    /**
     * Takes the searchbar value and updates the graph to focus on that person
     * The person to focus on has already been validated that they are in the
     * graph by the validation function in Controls.
     * @param person_to_focus The person we want the graph to focus on
     */
    handle_searchbar_search_and_focus_grpah(person_to_focus) {
        let data = this.state.data;
        const config = this.state.config;
        // update center names to selected node
        // turning the next two lines into a one-liner gives an error. unclear why.
        data.center_names = {};
        data.center_names[person_to_focus] = true;

        config.selection_active = true;
        config.selection_name = person_to_focus;
        config.show_info_panel = true;
        config.searchbar_value = person_to_focus;
        config.viz_update_func = 'update_focus';
        const person = this.get_person_data(person_to_focus);
        config.person_to_display_info = person;
        data = update_node_degree_and_visibility(data, config, person_to_focus);
        this.setState({data: data, config: config});
    }

    /**
     * Handles clearing the searchbar when the "clear (x) button is clicked
     * while also unfocuses the graph such that it returns to its original
     * state.
     */
    handle_searchbar_clear_and_unfocus_graph() {

        const config = this.state.config;
        let data = this.state.data;
        data.center_names = data.center_names_backup;
        config.searchbar_value = "";
        config.selection_active = false;
        config.selection_name = undefined;
        config.show_info_panel = false;
        config.viz_update_func = 'update_focus';
        data = update_node_degree_and_visibility(
            data, config);
        config.person_to_display_info = {name: "", affiliation: "", docs: 0};
        this.setState({data: data, config: config});
    }


    /**
     * Handles a visualization event
     *
     * @param event_name: String
     * @param data: Object
     */
    handle_viz_events(event_name, data) {


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
            // select new person
            if (!config.selection_active || node.name !== this.state.config.selection_name){
                this.handle_searchbar_search_and_focus_grpah(node.name);

            } else {
                this.handle_searchbar_clear_and_unfocus_graph();
            }
        }
    }

    update_searchbar_value(search_string) {
        const config = {...this.state.config};
        if (search_string !== null) {
            config.searchbar_value = search_string;
        } else {
            config.searchbar_value = "";
        }

        this.setState({config: config});
    }

    submitFormHandler = event => {
        event.preventDefault();
    };

    update_dataset(dataset_name) {
        const config = this.state.config;
        config.dataset_name = dataset_name;
        config.viz_update_func = 'create_graph';
        config.person_to_display_info = {name: "", affiliation: "", docs: 0};
        this.load_dataset(config.dataset_name);
        config.searchbar_value = "";
        config.selection_active = false;
        config.selection_name = undefined;
        config.show_info_panel = false;
        //setting update to undefined after loading to prevent infinite loop of
        // update -> setting data bindings -> update
        config.viz_update_func = undefined;

        this.setState({data: null, config: config});
    }

    async load_dataset(dataset_name) {
        const dataset = encodeURIComponent(dataset_name);
        fetch(`get_network_data?dataset=${dataset}`)
            .then((response) => {
                response
                    .json()
                    .then((data) => {
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
                        handle_searchbar_search_and_focus_grpah={(search_string) =>
                            this.handle_searchbar_search_and_focus_grpah(search_string)}
                        handle_searchbar_clear_and_unfocus_graph={() =>
                            this.handle_searchbar_clear_and_unfocus_graph()}
                        handle_viz_events={(event_name, data) =>
                            this.handle_viz_events(event_name, data )}
                        update_searchbar_value={(e) => this.update_searchbar_value(e)}
                        toggle_show_table={() => this.toggle_show_table()}
                        cluster_nodes={this.state.config.cluster_nodes}
                        nodes={this.state.data.nodes}
                        searchbar_value={this.state.config.searchbar_value}
                        dataset_name={this.state.config.dataset_name}
                        update_dataset={
                            (dataset_name) => this.update_dataset(dataset_name)
                        }
                        data_names={this.state.data.nodes}
                        show_dataset_selector={this.state.config.show_dataset_selector}

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
                                person={this.state.config.person_to_display_info}
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
MainView.propTypes ={
    dataset_name: PropTypes.string,
    show_dataset_selector: PropTypes.bool.isRequired,
    element_for_graph_sizing: PropTypes.string.isRequired
};


// when importing Main what do we get?
export default MainView;
