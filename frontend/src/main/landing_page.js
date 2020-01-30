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
            <li className={"nav_selector"}>
                <a className={"nav_selector_link"} href={this.props.url}>
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

export class LandingView extends React.Component {
    constructor(props){
        super(props);
    }

    render(){
        const content =
            <>
                <div className="container">
                    <div className="col-12">
                        <h1 className="display-2 title">Tobacco Networks</h1>
                        {/*<h1>Tobacco Networks</h1>*/}
                        <h1 className="subtitle">The Industry’s Correspondence Networks
                            at a
                            Glance</h1>
                        <p>
                            During the 20th century, the tobacco industry wasn’t just another
                            industry—it was a kraken, reaching into every aspect of the lives of
                            Americans. Lobbyists argued against smoking bans by framing smoking as
                            a free and personal choice. Marketers figured out ever new ways of
                            selling cigarettes to children. Scientists, secretly in the industry’s
                            employ went on TV and in front of congress to claim that there are still
                            doubts about smoking’s health harms. Lawyers deployed scorched-earth
                            tactics against anyone trying to sue them. Meanwhile, celebrity
                            spokespeople hawked ever new cigarette brands in magazines and on
                            billboards.
                        </p>
                        <p>
                            How did cigarette makers coordinate this network of executives,
                            researchers, and marketers? How did Philip Morris, R.J. Reynolds, and
                            the other major American tobacco companies synchronize their legal
                            strategies? To explore these questions, we have taken the 1.4 million
                            tobacco industry documents from the 1970s and turned them into a
                            network graph.
                        </p>
                        <p>On this page, you can:</p>


                        <ul role="tablist" id="nav_selectors_list">
                            <NavSelector
                                url="/explore_networks/"
                                img_url='/static/img/nav/explore_networks.png'
                                title='Network Exploration'
                                description='Explore the social networks of industry research
                                directors and lawyers'
                            />
                            <NavSelector
                                url="/explore_networks/"
                                img_url='/static/img/nav/explore_networks.png'
                                title='Network Exploration'
                                description='Explore the social networks of industry research
                                directors and lawyers'
                            />
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
