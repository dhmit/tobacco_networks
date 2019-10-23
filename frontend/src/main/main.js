/**
 * UI Code for the visualization
 */
import React from 'react';
import PropTypes from 'prop-types';

import { getCookie } from '../common'
import { create_graph, update_graph_color } from './graph.js'
import './main.css';

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
                        this.setState({data:data});
                    })
            }).catch(() => {
                console.log("error");
            });
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
                        <Viz
                            data={this.state.data}
                            config={this.state.config}
                            handle_viz_events={(event_name, data) =>
                                this.handle_viz_events(event_name, data )}
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
