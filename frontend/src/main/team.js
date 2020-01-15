import React from 'react';
import MainLayout from "./main_layout";
//import MainLayout from "./main_layout";

export class TeamView extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <MainLayout
                content={
                    <div>
                        <div className="row">
                            <h1>About this Project</h1>
                        </div>
                        <div className="row">
                            <h1>UROP Members</h1>
                        </div>
                        <div  className="row">
                            <h1>Staff</h1>
                        </div>
                    </div>

                }
            />
        )
    }
}

export default TeamView;
