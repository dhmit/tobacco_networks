import React from 'react';
import MainLayout from "./main_layout";
import PropTypes from "prop-types";

import './landing_page.css'


class NavSelector extends React.Component {
    constructor(props){
        super(props);
    }

    render(){
        return(
            <li>
                <a href={this.props.url}>
                    <img className="nav_selector_img" src={this.props.img_url} alt=""/>
                    <div className="nav_selector_title">
                        <h4>{this.props.title}</h4>
                    </div>
                    <p>{this.props.description}</p>
                </a>
            </li>
        )
    }
}
NavSelector.propTypes = {
    url: PropTypes.string.isRequired,
    img_url: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired
};

//
// <li>
//     <a href="/case/ctr">
//         <img className="team_member_image"
//              src="{{ url_for('static', filename='images/case_study_ctr_thumbnail.jpg') }}">
//             <div className="case_studies_title">
//                 <h4>Manufacturing Doubt</h4>
//                 <h5>Distraction and Subversion Research at the Council for Tobacco Research</h5>
//             </div>
//
//          <p> The Council for Tobacco Research (CTR) was at the center of the industry's efforts
//                 to produce
//                 doubts about smoking's health harms. This essay explores how the CTR pursued this
//                 goal by drawing on more than 10,000
//                 CTR grant applications and 140 Special Projects.
//             </p>
//     </a>
// </li>

export class LandingView extends React.Component {
    constructor(props){
        super(props);
    }

    render(){
        const content =
            <>
                <div className="container">
                    <div className="col-12">
                        <h1>Tobacco Networks</h1>
                        <h2>The  industry’s correspondence networks at a glance</h2>


                        <ul className="nav nav-pills" role="tablist" id="nav_selectors_list">
                            <NavSelector
                                url="/explore_networks/"
                                img_url='/static/img/nav/explore_networks.png'
                                title='Network Exploration'
                                description='Explore the social networks of industry research
                                directors and lawyers'
                            />
                        </ul>

                    </div>
                </div>
            </>;

        console.log(content);
        return(
            <MainLayout
                content={content}
            />
        )
    }
}

export default LandingView;
