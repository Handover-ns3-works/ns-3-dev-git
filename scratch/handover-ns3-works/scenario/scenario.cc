/*
 * Copyright (c) 2013 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: Manuel Requena <manuel.requena@cttc.es>
 */

#include "ns3/applications-module.h"
#include "ns3/channel-condition-model.h"
#include "ns3/config-store-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/lte-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/propagation-loss-model.h"
using namespace ns3;

NS_LOG_COMPONENT_DEFINE("LenaX2HandoverMeasures");

void
NotifyConnectionEstablishedUe(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    std::cout << context << " UE IMSI " << imsi << ": connected to CellId " << cellid
              << " with RNTI " << rnti << std::endl;
}

void
NotifyHandoverStartUe(std::string context,
                      uint64_t imsi,
                      uint16_t cellid,
                      uint16_t rnti,
                      uint16_t targetCellId)
{
    std::cout << context << " UE IMSI " << imsi << ": previously connected to CellId " << cellid
              << " with RNTI " << rnti << ", doing handover to CellId " << targetCellId
              << std::endl;
}

double g_HO_count = 0;

void
NotifyHandoverEndOkUe(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    g_HO_count++;
    std::cout << Simulator::Now().GetSeconds() << "\tHandover_ok for IMSI " << imsi << std::endl;
    // std::cout << context << " UE IMSI " << imsi << ": successful handover to CellId " << cellid
    //           << " with RNTI " << rnti << std::endl;
}

void
NotifyConnectionEstablishedEnb(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    std::cout << context << " eNB CellId " << cellid << ": successful connection of UE with IMSI "
              << imsi << " RNTI " << rnti << std::endl;
}

void
NotifyHandoverStartEnb(std::string context,
                       uint64_t imsi,
                       uint16_t cellid,
                       uint16_t rnti,
                       uint16_t targetCellId)
{
    std::cout << context << " eNB CellId " << cellid << ": start handover of UE with IMSI " << imsi
              << " RNTI " << rnti << " to CellId " << targetCellId << std::endl;
}

void
NotifyHandoverEndOkEnb(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    std::cout << context << " eNB CellId " << cellid << ": completed handover of UE with IMSI "
              << imsi << " RNTI " << rnti << std::endl;
}

double g_RLF_count = 0;
// List of simulation time when RLF occurs
std::vector<double> g_RLF_time;

void
RadioLinkFailureCallback(std::string context, uint64_t imsi, uint16_t cellId, uint16_t rnti)
{
    std::cout << Simulator::Now().GetSeconds() << "\tRLF occurred for IMSI " << imsi << std::endl;
    g_RLF_count++;
    g_RLF_time.push_back(Simulator::Now().GetSeconds());
}

double g_HOF_count = 0;

void
NotifyHandoverFailure(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    g_HOF_count++;
    std::cout << Simulator::Now().As(Time::S) << " " << context << " eNB CellId " << cellid
              << " IMSI " << imsi << " RNTI " << rnti << " handover failure" << std::endl;
}

void
CourseChangeCallback(std::string context, Ptr<const MobilityModel> model)
{
	Vector position = model->GetPosition();
	std::cout << Simulator::Now().GetSeconds() << " Position: " <<	context <<
		" x = " << position.x << ", y = " << position.y << std::endl;
}

/**
 * Sample simulation script for an automatic X2-based handover based on the RSRQ measures.
 * It instantiates two eNodeB, attaches one UE to the 'source' eNB.
 * The UE moves between both eNBs, it reports measures to the serving eNB and
 * the 'source' (serving) eNB triggers the handover of the UE towards
 * the 'target' eNB when it considers it is a better eNB.
 */
int
main(int argc, char* argv[])
{
    Time::SetResolution(Time::NS);

    uint16_t numberOfUes = 10;
    uint16_t numberOfEnbs = 2;
    uint16_t numBearersPerUe = 0;
    double distance = 100.0; // m
    // double yForUe = 30.0;                                           // m
    double speed = 20, angleInDegrees = 0;
    double simTime = (double)(numberOfEnbs + 1) * distance / speed; // 1500 m / 20 m/s = 75 secs
    double enbTxPowerDbm = 46.0;
    double hysterisis = 3, timeToTrigger = 256;
		double servingCellThreshold = 30, neighbourCellOffset = 1;
    double Qout = -5, Qin = -3.9;
    double T310 = 1000, N310 = 6, N311 = 2;
    std::vector<double> Ue_ycoord = {30, 29, 28, 27, 26, -30, -29, -28, -27, -26};
		// 0 = DETERMINISTIC, 1 = RAYLEIGH, 2 = CORRELATED
		double fadingModel = 0;
		// 0 = A3, 1 = A2A4
		double handoverAlgorithm = 0;
		
		uint16_t useRandomWaypoint = 0;
		double XMax = 300.0, YMax = 1500.0;
		double nodeSpeed = 20, nodePause = 0;
		
		std::string enbCoordinatesString = "0,0,0,100,0,0";

    // change some default attributes so that they are reasonable for
    // this scenario, but do this before processing command line
    // arguments, so that the user is allowed to override these settings
    Config::SetDefault("ns3::UdpClient::Interval", TimeValue(MilliSeconds(10)));
    Config::SetDefault("ns3::UdpClient::MaxPackets", UintegerValue(1000000));
    Config::SetDefault("ns3::LteHelper::UseIdealRrc", BooleanValue(true));

    // Command line arguments
    CommandLine cmd(__FILE__);
    cmd.AddValue("simTime", "Total duration of the simulation (in seconds)", simTime);
		cmd.AddValue("enbCoordinatesString", "Positive coordinates of the eNBs (in format x0,y0,z0,x1,y1,z1 ...)", enbCoordinatesString);
    cmd.AddValue("speed", "Speed of the UE (default = 20 m/s)", speed);
    cmd.AddValue("enbTxPowerDbm", "TX power [dBm] used by HeNBs (default = 46.0)", enbTxPowerDbm);
    cmd.AddValue("hysteresis",
                 "Hysterisis value for A3 handover algorithm (default = 3.0 dB)",
                 hysterisis);
    cmd.AddValue("timeToTrigger",
                 "Time to trigger value for A3 handover algorithm (default = 0.256 s)",
                 timeToTrigger);
		cmd.AddValue("servingCellThreshold", "Serving Cell Threshold for A2A4 handover algorithm (default = 30)", servingCellThreshold);
		cmd.AddValue("neighbourCellOffset", "Neighbour Cell Offset for A2A4 handover algorithm (default = 1)", neighbourCellOffset);
    cmd.AddValue("numberOfUes", "Number of UEs (default = 10)", numberOfUes);
		cmd.AddValue("angle", "Angle made by the UEs with the X-Axis (default = 0 degrees)", angleInDegrees);
		cmd.AddValue("Qout", "Qout value for lte-ue-phy (default = -5 dB)", Qout);
		cmd.AddValue("Qin", "Qin value for lte-ue-phy (default = -3.9 dB)", Qin);
		cmd.AddValue("T310", "T310 value for lte-ue-rrc (default = 1000 ms)", T310);
		cmd.AddValue("N310", "N310 value for lte-ue-phy (default = 6)", N310);
		cmd.AddValue("N311", "N311 value for lte-ue-phy (default = 2)", N311);
		cmd.AddValue("fadingModel", "Fading model to be used (default = DETERMINISTIC)", fadingModel);
		cmd.AddValue("handoverAlgorithm", "Handover algorithm to be used (default = A3)", handoverAlgorithm);
		
		cmd.AddValue("useRandomWaypoint", "Use Random Waypoint Mobility Model for UE", useRandomWaypoint);
		cmd.AddValue("randomRectanglePositionAllocatorXMax", "The maximum value for the UniformRandomVariable for X", XMax);
		cmd.AddValue("randomRectanglePositionAllocatorYMax", "The maximum value for the UniformRandomVariable for Y", YMax);
		cmd.AddValue("randomWaypointMobilityModelSpeed", "Max speed value for UniformRandomVariable", nodeSpeed);
		cmd.AddValue("randomWaypointMobilityModelPause", "Max pause value for UniformRandomVariable", nodePause);

    cmd.Parse(argc, argv);
    double angleInRadians = angleInDegrees * M_PI / 180.0;
		// split the string into tokens and store the values in a vector
		std::vector<std::string> enbCoordinates;
		std::stringstream ss(enbCoordinatesString);
    std::string token;
    while (std::getline(ss, token, ',')) {
        enbCoordinates.push_back(token);
    }
		numberOfEnbs = enbCoordinates.size() / 3;

    Ptr<LteHelper> lteHelper = CreateObject<LteHelper>();
    Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper>();
    lteHelper->SetEpcHelper(epcHelper);
    lteHelper->SetSchedulerType("ns3::RrFfMacScheduler");

		if( handoverAlgorithm == 0 ) {
			lteHelper->SetHandoverAlgorithmType("ns3::A3RsrpHandoverAlgorithm");
			lteHelper->SetHandoverAlgorithmAttribute("Hysteresis", DoubleValue(hysterisis));
			lteHelper->SetHandoverAlgorithmAttribute("TimeToTrigger",
																							TimeValue(MilliSeconds(timeToTrigger)));
		} else {
			lteHelper->SetHandoverAlgorithmType("ns3::A2A4RsrqHandoverAlgorithm");
			lteHelper->SetHandoverAlgorithmAttribute("ServingCellThreshold", UintegerValue(servingCellThreshold));
			lteHelper->SetHandoverAlgorithmAttribute("NeighbourCellOffset", UintegerValue(neighbourCellOffset));
		}															

    // Correlated
		if( fadingModel == 2 ) {
			std::cout << "Using Correlated fading model" << std::endl;
			Ptr<ChannelConditionModel> condModel = CreateObject<ThreeGppUmaChannelConditionModel> ();
			lteHelper->SetAttribute ("PathlossModel", StringValue
			("ns3::ThreeGppUmaPropagationLossModel")); lteHelper->SetPathlossModelAttribute
			("ChannelConditionModel", PointerValue (condModel));
		}

    Ptr<Node> pgw = epcHelper->GetPgwNode();

    // Create a single RemoteHost
    NodeContainer remoteHostContainer;
    remoteHostContainer.Create(1);
    Ptr<Node> remoteHost = remoteHostContainer.Get(0);
    InternetStackHelper internet;
    internet.Install(remoteHostContainer);

    // Create the Internet
    PointToPointHelper p2ph;
    p2ph.SetDeviceAttribute("DataRate", DataRateValue(DataRate("100Gb/s")));
    p2ph.SetDeviceAttribute("Mtu", UintegerValue(1500));
    p2ph.SetChannelAttribute("Delay", TimeValue(Seconds(0.010)));
    NetDeviceContainer internetDevices = p2ph.Install(pgw, remoteHost);
    Ipv4AddressHelper ipv4h;
    ipv4h.SetBase("1.0.0.0", "255.0.0.0");
    Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign(internetDevices);
    Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress(1);

    // Routing of the Internet Host (towards the LTE network)
    Ipv4StaticRoutingHelper ipv4RoutingHelper;
    Ptr<Ipv4StaticRouting> remoteHostStaticRouting =
        ipv4RoutingHelper.GetStaticRouting(remoteHost->GetObject<Ipv4>());
    // interface 0 is localhost, 1 is the p2p device
    remoteHostStaticRouting->AddNetworkRouteTo(Ipv4Address("7.0.0.0"), Ipv4Mask("255.0.0.0"), 1);

    /*
     * Network topology:
     *
     *      |     + --------------------------------------------------------->
     *      |     UE
     *    y |
     *      | (0, 0, 0)     d                   d
     *      |     o-------------------x-------------------
     *          eNodeB              eNodeB											d = distance
     *            						                                  y = yForUe
     */

    NodeContainer ueNodes;
    NodeContainer enbNodes;
    enbNodes.Create(numberOfEnbs);
    ueNodes.Create(numberOfUes);
		
    // Install Mobility Model in eNB
    Ptr<ListPositionAllocator> enbPositionAlloc = CreateObject<ListPositionAllocator>();
    for (uint16_t i = 0; i < numberOfEnbs; i++)
    {
        Vector enbPosition = Vector(atoi(enbCoordinates[i*3].c_str()), atoi(enbCoordinates[i*3+1].c_str()), atoi(enbCoordinates[i*3+2].c_str()));
        enbPositionAlloc->Add(enbPosition);
    }

    MobilityHelper enbMobility;
    enbMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    enbMobility.SetPositionAllocator(enbPositionAlloc);
    enbMobility.Install(enbNodes);

    // Install Mobility Model in UE
    MobilityHelper ueMobility;
		if( useRandomWaypoint == 1 ) {
			int64_t streamIndex = 0; // used to get consistent mobility across scenarios
			ObjectFactory pos;
			pos.SetTypeId("ns3::RandomRectanglePositionAllocator");
			pos.Set("X", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=" + std::to_string(XMax) + "]"));
			pos.Set("Y", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=" + std::to_string(YMax) + "]"));

			Ptr<PositionAllocator> taPositionAlloc = pos.Create()->GetObject<PositionAllocator>();
			streamIndex += taPositionAlloc->AssignStreams(streamIndex);

			std::stringstream ssSpeed;
			ssSpeed << "ns3::UniformRandomVariable[Min=0.0|Max=" << nodeSpeed << "]";
			std::stringstream ssPause;
			ssPause << "ns3::ConstantRandomVariable[Constant=" << nodePause << "]";
			ueMobility.SetMobilityModel("ns3::RandomWaypointMobilityModel",
																		"Speed",
																		StringValue(ssSpeed.str()),
																		"Pause",
																		StringValue(ssPause.str()),
																		"PositionAllocator",
																		PointerValue(taPositionAlloc));
			ueMobility.SetPositionAllocator(taPositionAlloc);
			ueMobility.Install(ueNodes);
			streamIndex += ueMobility.AssignStreams(ueNodes, streamIndex);
		} else {
			ueMobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
			ueMobility.Install(ueNodes);
			for (uint16_t i = 0; i < numberOfUes; i++)
			{
					double vx = speed * std::cos(angleInRadians);
					double vy = speed * std::sin(angleInRadians);
					ueNodes.Get(i)->GetObject<ConstantVelocityMobilityModel>()->SetPosition(
							Vector(0, Ue_ycoord[i], 0));
					ueNodes.Get(i)->GetObject<ConstantVelocityMobilityModel>()->SetVelocity(Vector(vx, vy, 0));
			}
		}

    // Install LTE Devices in eNB and UEs
    // lteHelper->SetEnbDeviceAttribute("DlEarfcn", UintegerValue (6250));
    // lteHelper->SetUeDeviceAttribute("DlEarfcn", UintegerValue (6250));
    lteHelper->SetAttribute("UsePdschForCqiGeneration", BooleanValue(false));
    Config::SetDefault("ns3::LteEnbPhy::TxPower", DoubleValue(enbTxPowerDbm));
		
		// How to set global attribute values from cmd: https://www.nsnam.org/docs/manual/html/attributes.html
		Config::SetDefault("ns3::LteUePhy::Qout", DoubleValue(Qout));
		Config::SetDefault("ns3::LteUePhy::Qin", DoubleValue(Qin));
		Config::SetDefault("ns3::LteUeRrc::T310", TimeValue(MilliSeconds(T310)));
		Config::SetDefault("ns3::LteUeRrc::N310", UintegerValue(N310));
		Config::SetDefault("ns3::LteUeRrc::N311", UintegerValue(N311));
		
    NetDeviceContainer enbLteDevs = lteHelper->InstallEnbDevice(enbNodes);
    // Change the txPower for just the interference nodes
    // Config::SetDefault("ns3::LteEnbPhy::TxPower", DoubleValue(20.0));
    NetDeviceContainer ueLteDevs = lteHelper->InstallUeDevice(ueNodes);

    // Install the IP stack on the UEs
    internet.Install(ueNodes);
    Ipv4InterfaceContainer ueIpIfaces;
    ueIpIfaces = epcHelper->AssignUeIpv4Address(NetDeviceContainer(ueLteDevs));

    // Attach all UEs to the first eNodeB
    for (uint16_t i = 0; i < numberOfUes; i++)
    {
        lteHelper->Attach(ueLteDevs.Get(i), enbLteDevs.Get(0));
    }

    NS_LOG_LOGIC("setting up applications");

    // Install and start applications on UEs and remote host
    uint16_t dlPort = 10000;
    uint16_t ulPort = 20000;

    // randomize a bit start times to avoid simulation artifacts
    // (e.g., buffer overflows due to packet transmissions happening
    // exactly at the same time)
    Ptr<UniformRandomVariable> startTimeSeconds = CreateObject<UniformRandomVariable>();
    startTimeSeconds->SetAttribute("Min", DoubleValue(0));
    startTimeSeconds->SetAttribute("Max", DoubleValue(0.010));

    for (uint32_t u = 0; u < numberOfUes; ++u)
    {
        Ptr<Node> ue = ueNodes.Get(u);
        // Set the default gateway for the UE
        Ptr<Ipv4StaticRouting> ueStaticRouting =
            ipv4RoutingHelper.GetStaticRouting(ue->GetObject<Ipv4>());
        ueStaticRouting->SetDefaultRoute(epcHelper->GetUeDefaultGatewayAddress(), 1);

        for (uint32_t b = 0; b < numBearersPerUe; ++b)
        {
            ++dlPort;
            ++ulPort;

            ApplicationContainer clientApps;
            ApplicationContainer serverApps;

            NS_LOG_LOGIC("installing UDP DL app for UE " << u);
            UdpClientHelper dlClientHelper(ueIpIfaces.GetAddress(u), dlPort);
            clientApps.Add(dlClientHelper.Install(remoteHost));
            PacketSinkHelper dlPacketSinkHelper("ns3::UdpSocketFactory",
                                                InetSocketAddress(Ipv4Address::GetAny(), dlPort));
            serverApps.Add(dlPacketSinkHelper.Install(ue));

            NS_LOG_LOGIC("installing UDP UL app for UE " << u);
            UdpClientHelper ulClientHelper(remoteHostAddr, ulPort);
            clientApps.Add(ulClientHelper.Install(ue));
            PacketSinkHelper ulPacketSinkHelper("ns3::UdpSocketFactory",
                                                InetSocketAddress(Ipv4Address::GetAny(), ulPort));
            serverApps.Add(ulPacketSinkHelper.Install(remoteHost));

            Ptr<EpcTft> tft = Create<EpcTft>();
            EpcTft::PacketFilter dlpf;
            dlpf.localPortStart = dlPort;
            dlpf.localPortEnd = dlPort;
            tft->Add(dlpf);
            EpcTft::PacketFilter ulpf;
            ulpf.remotePortStart = ulPort;
            ulpf.remotePortEnd = ulPort;
            tft->Add(ulpf);
            EpsBearer bearer(EpsBearer::NGBR_VIDEO_TCP_DEFAULT);
            lteHelper->ActivateDedicatedEpsBearer(ueLteDevs.Get(u), bearer, tft);

            Time startTime = Seconds(startTimeSeconds->GetValue());
            serverApps.Start(startTime);
            clientApps.Start(startTime);

        } // end for b
    }

    // Add X2 interface
    lteHelper->AddX2Interface(enbNodes);

    if( fadingModel == 1 ) {
			std::cout << "Using Rayleigh fading model" << std::endl;
			Ptr<NakagamiPropagationLossModel> propModel = CreateObject<NakagamiPropagationLossModel>();
			propModel->SetAttribute("m0", DoubleValue(1));
			propModel->SetAttribute("m1", DoubleValue(1));
			propModel->SetAttribute("m2", DoubleValue(1));
			lteHelper->GetDownlinkSpectrumChannel()->AddPropagationLossModel(propModel);
			lteHelper->GetUplinkSpectrumChannel()->AddPropagationLossModel(propModel);
		}

    // lteHelper->EnablePhyTraces();

    // connect custom trace sinks for RRC connection establishment and handover notification
    // Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/ConnectionEstablished",
    //                 MakeCallback(&NotifyConnectionEstablishedEnb));
    // Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/ConnectionEstablished",
    //                 MakeCallback(&NotifyConnectionEstablishedUe));
    // Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverStart",
    //                 MakeCallback(&NotifyHandoverStartEnb));
    // Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/HandoverStart",
    //                 MakeCallback(&NotifyHandoverStartUe));
    // Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverEndOk",
    //                 MakeCallback(&NotifyHandoverEndOkEnb));
    Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndOk",
                    MakeCallback(&NotifyHandoverEndOkUe));
    Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/RadioLinkFailure",
                    MakeCallback(&RadioLinkFailureCallback));
		Config::Connect("/NodeList/*/$ns3::MobilityModel/CourseChange",
										MakeCallback(&CourseChangeCallback));

    // Hook a trace sink (the same one) to the four handover failure traces
    // Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureNoPreamble",
    //                 MakeCallback(&NotifyHandoverFailure));
    // Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureMaxRach",
    //                 MakeCallback(&NotifyHandoverFailure));
    // Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureLeaving",
    //                 MakeCallback(&NotifyHandoverFailure));
    // Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureJoining",
    //                 MakeCallback(&NotifyHandoverFailure));
    // Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndError",
    // 								MakeCallback(&NotifyHandoverFailure));

    Simulator::Stop(Seconds(simTime));
    Simulator::Run();

    Simulator::Destroy();
    // std::cout << "RLF count: " << g_RLF_count << std::endl;
    // for (auto i = g_RLF_time.begin(); i != g_RLF_time.end(); ++i)
    // {
    // 	std::cout << "RLF time: " << *i << std::endl;
    // }
    // std::cout << "HO count: " << g_HO_count << std::endl;
    // std::cout << "HOF count: " << g_HOF_count << std::endl;
    return 0;
}
