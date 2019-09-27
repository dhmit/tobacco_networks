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
        this._graph = create_graph(
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
Viz.propTypes = {
    data: PropTypes.arrayOf(PropTypes.object).isRequired,
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
                <p>Your mouse is {this.props.mouseover ? 'OVER' : 'NOT OVER'}  a bar on the viz!</p>
                <p>The current viz color is {this.props.currentColor}</p>
            </div>
        );
    }
}
Info.propTypes ={
    mouseover: PropTypes.bool,
    currentColor: PropTypes.string,
};


/***************************************************************************************************
 * Main component for the main view.
 **************************************************************************************************/
class MainView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            config: {
                width: 500,
                height: 500,
                color: 'blue',
            },  // initial configuration for the viz
            data: null,  // data for the viz
            mouseover: false,  // info panel state (based on callbacks from viz)
        };
        this.csrftoken = getCookie('csrftoken');
    }

    componentDidMount() {
        fetch("api/people/")
            .then((response) => {
                // console.log(response);
                response
                    .json()
                    .then((data) => {
                        this.setState({data});
                        // console.log(data);
                    })
            }).catch(() => {
                console.log("error");
            });
    }

    handle_checkbox() {
        const config = {...this.state.config};  // ... is the 'spread' operator - this is a copy
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

    handle_viz_events(event_name) {
        if (event_name === "mouseover") {
            this.setState({mouseover: true});
        } else if (event_name === "mouseout") {
            this.setState({mouseover: false});
        }
    }

    render() {
        if (this.state.data) {
            return (
                <div className="container">
                    <div className="row">
                        <Controls
                            handle_checkbox={() => this.handle_checkbox()}
                            config={this.state.config}
                        />
                        <Viz
                            data={this.state.data}
                            config={this.state.config}
                            handle_viz_events={(event_name) => this.handle_viz_events(event_name)}
                        />
                        <Info
                            mouseover={this.state.mouseover}
                            currentColor={this.state.config.color}
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

export default MainView;
