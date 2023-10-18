#include "ns3/applications-module.h"
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

// Global variables
uint16_t counterN310FirsteNB = 0;        // Counter for N310 first eNB
Time t310StartTimeFirstEnb = Seconds(0); //!< Time of first N310 indication.

/// Map each of UE RRC states to its string representation.
static const std::string g_ueRrcStateName[LteUeRrc::NUM_STATES] = {
    "IDLE_START",
    "IDLE_CELL_SEARCH",
    "IDLE_WAIT_MIB_SIB1",
    "IDLE_WAIT_MIB",
    "IDLE_WAIT_SIB1",
    "IDLE_CAMPED_NORMALLY",
    "IDLE_WAIT_SIB2",
    "IDLE_RANDOM_ACCESS",
    "IDLE_CONNECTING",
    "CONNECTED_NORMALLY",
    "CONNECTED_HANDOVER",
    "CONNECTED_PHY_PROBLEM",
    "CONNECTED_REESTABLISHING",
};

/**
 * UE Notify connection established.
 *
 * \param context The context.
 * \param imsi The IMSI.
 * \param cellid The Cell ID.
 * \param rnti The RNTI.
 */
void
NotifyConnectionEstablishedUe(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    std::cout << Simulator::Now().As(Time::S) << " " << context << " UE IMSI " << imsi
              << ": connected to cell id " << cellid << " with RNTI " << rnti << std::endl;
}

/**
 * \param s The UE RRC state.
 * \return The string representation of the given state.
 */
static const std::string&
ToString(LteUeRrc::State s)
{
    return g_ueRrcStateName[s];
}

/**
 * eNB Notify connection established.
 *
 * \param context The context.
 * \param imsi The IMSI.
 * \param cellId The Cell ID.
 * \param rnti The RNTI.
 */
void
NotifyConnectionEstablishedEnb(std::string context, uint64_t imsi, uint16_t cellId, uint16_t rnti)
{
    std::cout << Simulator::Now().As(Time::S) << " " << context << " eNB cell id " << cellId
              << ": successful connection of UE with IMSI " << imsi << " RNTI " << rnti
              << std::endl;
    // In this example, a UE should experience RLF at least one time in
    // cell 1. For the case, when there is only one eNB with ideal RRC,
    // a UE might reconnects to the eNB multiple times due to more than
    // one RLF. To handle this, we reset the counter here so, even if the UE
    // connects multiple time to cell 1 we count N310
    // indication correctly, i.e., for each RLF UE RRC should receive
    // configured number of N310 indications.
    if (cellId == 1)
    {
        counterN310FirsteNB = 0;
    }
}

/**
 * Print the position of a UE with given IMSI.
 *
 * \param imsi The IMSI.
 */
void
PrintUePosition(uint64_t imsi)
{
    for (auto it = NodeList::Begin(); it != NodeList::End(); ++it)
    {
        Ptr<Node> node = *it;
        int nDevs = node->GetNDevices();
        for (int j = 0; j < nDevs; j++)
        {
            Ptr<LteUeNetDevice> uedev = node->GetDevice(j)->GetObject<LteUeNetDevice>();
            if (uedev)
            {
                if (imsi == uedev->GetImsi())
                {
                    Vector pos = node->GetObject<MobilityModel>()->GetPosition();
                    std::cout << "IMSI : " << uedev->GetImsi() << " at " << pos.x << "," << pos.y
                              << std::endl;
                }
            }
        }
    }
}

/**
 * Radio link failure tracer.
 *
 * \param t310 310 data.
 * \param imsi The IMSI.
 * \param cellId The Cell ID.
 * \param rnti The RNTI.
 */
void
RadioLinkFailure(Time t310, uint64_t imsi, uint16_t cellId, uint16_t rnti)
{
    std::cout << Simulator::Now() << " IMSI " << imsi << ", RNTI " << rnti << ", Cell id " << cellId
              << ", radio link failure detected" << std::endl
              << std::endl;

    PrintUePosition(imsi);

    if (cellId == 1)
    {
        NS_ABORT_MSG_IF((Simulator::Now() - t310StartTimeFirstEnb) != t310,
                        "T310 timer expired at wrong time");
    }
}

/**
 * UE state transition tracer.
 *
 * \param imsi The IMSI.
 * \param cellId The Cell ID.
 * \param rnti The RNTI.
 * \param oldState The old state.
 * \param newState The new state.
 */
void
UeStateTransition(uint64_t imsi,
                  uint16_t cellId,
                  uint16_t rnti,
                  LteUeRrc::State oldState,
                  LteUeRrc::State newState)
{
    std::cout << Simulator::Now().As(Time::S) << " UE with IMSI " << imsi << " RNTI " << rnti
              << " connected to cell " << cellId << " transitions from " << ToString(oldState)
              << " to " << ToString(newState) << std::endl;
}

/**
 * eNB RRC timeout tracer.
 *
 * \param imsi The IMSI.
 * \param rnti The RNTI.
 * \param cellId The Cell ID.
 * \param cause The reason for timeout.
 */
void
EnbRrcTimeout(uint64_t imsi, uint16_t rnti, uint16_t cellId, std::string cause)
{
    std::cout << Simulator::Now().As(Time::S) << " IMSI " << imsi << ", RNTI " << rnti
              << ", Cell id " << cellId << ", ENB RRC " << cause << std::endl;
}

/**
 * Handover failure notification
 *
 * \param context The context.
 * \param imsi The IMSI of the connected terminal.
 * \param cellid The Cell ID.
 * \param rnti The RNTI.
 */
void
NotifyHandoverFailure(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    std::cout << Simulator::Now().As(Time::S) << " " << context << " eNB CellId " << cellid
              << " IMSI " << imsi << " RNTI " << rnti << " handover failure" << std::endl;
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

void
NotifyHandoverEndOkUe(std::string context, uint64_t imsi, uint16_t cellid, uint16_t rnti)
{
    std::cout << context << " UE IMSI " << imsi << ": successful handover to CellId " << cellid
              << " with RNTI " << rnti << std::endl;
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

int
main(int argc, char* argv[])
{
    Time::SetResolution(Time::NS);

    /**
     * Physical Layer
     *
     *                                                                      10m/s
     * eNB4           eNB3           eNB2           eNB1           eNB0     <-- UE0
     *                                                                      <-- UE1
     *   x-------------x--------------x--------------x--------------x       <-- ...
     *        200m          200m           200m           200m              <-- UE8
     *                                                                      <-- UE9
     *
     */

    uint16_t numberOfUes = 10;               // No. of base stations
    uint16_t numberOfEnbs = 5;               // No. of mobile eNBs
    uint16_t numBearersPerUe = 0;            // No. of bearers per UE
    uint32_t m_handoverJoiningTimeout = 200; // ms
    uint32_t m_handoverLeavingTimeout = 500; // ms
    double interSiteDistance = 200.0;        // m
    double speed = 10.0;                     // m/s
    double enbTxPowerDbm = 30.0;             // dBm
    double hysterisis = 3.0;                 // dB
    double timeToTrigger = 0.5;              // s
    Time simTime = Seconds(75);              // seconds
    bool m_useIdealRrc = false;

    // Timers
    uint16_t n311 = 1;
    uint16_t n310 = 1;
    Time t310 = Seconds(1);

    // CommandLine cmd; // incase we want to change the above parameters from command line

    Ptr<LteHelper> lteHelper = CreateObject<LteHelper>();
    Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper>();
    lteHelper->SetEpcHelper(epcHelper);
    lteHelper->SetSchedulerType("ns3::RrFfMacScheduler");
    lteHelper->SetHandoverAlgorithmType("ns3::A3RsrpHandoverAlgorithm");
    lteHelper->SetHandoverAlgorithmAttribute("Hysteresis", DoubleValue(hysterisis));
    lteHelper->SetHandoverAlgorithmAttribute("TimeToTrigger",
                                             TimeValue(MilliSeconds(timeToTrigger)));
    lteHelper->SetAttribute("UseIdealRrc", BooleanValue(m_useIdealRrc));
    Config::SetDefault("ns3::LteEnbRrc::HandoverJoiningTimeoutDuration",
                       TimeValue(MilliSeconds(m_handoverJoiningTimeout)));
    Config::SetDefault("ns3::LteEnbRrc::HandoverLeavingTimeoutDuration",
                       TimeValue(MilliSeconds(m_handoverLeavingTimeout)));

    Config::SetDefault("ns3::LteEnbPhy::TxPower", DoubleValue(enbTxPowerDbm));

    // Radio link failure detection parameters
    Config::SetDefault("ns3::LteUeRrc::N310", UintegerValue(n310));
    Config::SetDefault("ns3::LteUeRrc::N311", UintegerValue(n311));
    Config::SetDefault("ns3::LteUeRrc::T310", TimeValue(t310));

    NS_LOG_INFO("Create the internet");
    Ptr<Node> pgw = epcHelper->GetPgwNode();

    NodeContainer remoteHostContainer;
    remoteHostContainer.Create(1);
    Ptr<Node> remoteHost = remoteHostContainer.Get(0);
    InternetStackHelper internet;
    internet.Install(remoteHostContainer);

    PointToPointHelper p2ph;
    p2ph.SetDeviceAttribute("DataRate", DataRateValue(DataRate("100Gb/s")));
    p2ph.SetDeviceAttribute("Mtu", UintegerValue(1500));
    p2ph.SetChannelAttribute("Delay", TimeValue(Seconds(0.010)));
    NetDeviceContainer internetDevices = p2ph.Install(pgw, remoteHost);

    // Routing of the Internet Host (towards the LTE network)
    Ipv4AddressHelper ipv4h;
    ipv4h.SetBase("1.0.0.0", "255.0.0.0");
    Ipv4InterfaceContainer internetIpIfaces = ipv4h.Assign(internetDevices);
    Ipv4Address remoteHostAddr = internetIpIfaces.GetAddress(1);
    Ipv4StaticRoutingHelper ipv4RoutingHelper;
    Ptr<Ipv4StaticRouting> remoteHostStaticRouting =
        ipv4RoutingHelper.GetStaticRouting(remoteHost->GetObject<Ipv4>());
    remoteHostStaticRouting->AddNetworkRouteTo(Ipv4Address("7.0.0.0"), Ipv4Mask("255.0.0.0"), 1);

    NS_LOG_INFO("Create eNodeB and UE nodes");
    NodeContainer enbNodes;
    NodeContainer ueNodes;
    enbNodes.Create(numberOfEnbs);
    ueNodes.Create(numberOfUes);

    NS_LOG_INFO("Assign mobility(Base Station)");
    Ptr<ListPositionAllocator> positionAllocEnb = CreateObject<ListPositionAllocator>();
    for (uint16_t i = 0; i < numberOfEnbs; i++)
    {
        positionAllocEnb->Add(Vector(interSiteDistance * i, 0, 0));
    }
    MobilityHelper mobility;
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.SetPositionAllocator(positionAllocEnb);
    mobility.Install(enbNodes);

    NS_LOG_INFO("Assign mobility(User Equipment)");
    Ptr<ListPositionAllocator> positionAllocUe = CreateObject<ListPositionAllocator>();
    for (int i = 0; i < numberOfUes; i++)
    {
        positionAllocUe->Add(Vector(200, 0, 0));
    }

    mobility.SetPositionAllocator(positionAllocUe);
    mobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel");
    mobility.Install(ueNodes);

    for (int i = 0; i < numberOfUes; i++)
    {
        ueNodes.Get(i)->GetObject<ConstantVelocityMobilityModel>()->SetVelocity(
            Vector(speed, 0.0, 0.0));
    }

    NS_LOG_INFO("Install LTE Devices in eNB and UEs and fix random number stream");
    NetDeviceContainer enbDevs;
    NetDeviceContainer ueDevs;

    int64_t randomStream = 1;
    enbDevs = lteHelper->InstallEnbDevice(enbNodes);
    randomStream += lteHelper->AssignStreams(enbDevs, randomStream);
    ueDevs = lteHelper->InstallUeDevice(ueNodes);
    randomStream += lteHelper->AssignStreams(ueDevs, randomStream);

    NS_LOG_INFO("Install the IP stack on the UEs");
    internet.Install(ueNodes);
    Ipv4InterfaceContainer ueIpIfaces;
    ueIpIfaces = epcHelper->AssignUeIpv4Address(NetDeviceContainer(ueDevs));

    NS_LOG_INFO("Attach a UE to a eNB");
    for (uint16_t i = 0; i < numberOfUes; i++)
    {
        lteHelper->Attach(ueDevs.Get(i), enbDevs.Get(0));
    }

    NS_LOG_INFO("Install and start applications on UEs and remote host");
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
            lteHelper->ActivateDedicatedEpsBearer(ueDevs.Get(u), bearer, tft);

            Time startTime = Seconds(startTimeSeconds->GetValue());
            serverApps.Start(startTime);
            clientApps.Start(startTime);

        } // end for b
    }

    // Add X2 interface
    lteHelper->AddX2Interface(enbNodes);

    Ptr<NakagamiPropagationLossModel> propModel = CreateObject<NakagamiPropagationLossModel>();
    propModel->SetAttribute("m0", DoubleValue(1));
    propModel->SetAttribute("m1", DoubleValue(1));
    propModel->SetAttribute("m2", DoubleValue(1));
    lteHelper->GetDownlinkSpectrumChannel()->AddPropagationLossModel(propModel);
    lteHelper->GetUplinkSpectrumChannel()->AddPropagationLossModel(propModel);

    NS_LOG_INFO("Enable Lte traces and connect custom trace sinks");
    lteHelper->EnableTraces();
    Ptr<RadioBearerStatsCalculator> rlcStats = lteHelper->GetRlcStats();
    rlcStats->SetAttribute("EpochDuration", TimeValue(Seconds(0.05)));
    Ptr<RadioBearerStatsCalculator> pdcpStats = lteHelper->GetPdcpStats();
    pdcpStats->SetAttribute("EpochDuration", TimeValue(Seconds(0.05)));

    // callback check for connection
    Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/ConnectionEstablished",
                    MakeCallback(&NotifyConnectionEstablishedEnb));
    Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/ConnectionEstablished",
                    MakeCallback(&NotifyConnectionEstablishedUe));

    // State transition
    Config::ConnectWithoutContext("/NodeList/*/DeviceList/*/LteUeRrc/StateTransition",
                                  MakeCallback(&UeStateTransition));
    Config::ConnectWithoutContext("/NodeList/*/DeviceList/*/LteUeRrc/RadioLinkFailure",
                                  MakeBoundCallback(&RadioLinkFailure, t310));

    // Handover failure
    Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverStart",
                    MakeCallback(&NotifyHandoverStartEnb));
    Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/HandoverStart",
                    MakeCallback(&NotifyHandoverStartUe));
    Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverEndOk",
                    MakeCallback(&NotifyHandoverEndOkEnb));
    Config::Connect("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndOk",
                    MakeCallback(&NotifyHandoverEndOkUe));
    // Hook a trace sink (the same one) to the four handover failure traces
    Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureNoPreamble",
                    MakeCallback(&NotifyHandoverFailure));
    Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureMaxRach",
                    MakeCallback(&NotifyHandoverFailure));
    Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureLeaving",
                    MakeCallback(&NotifyHandoverFailure));
    Config::Connect("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverFailureJoining",
                    MakeCallback(&NotifyHandoverFailure));

    // RRC
    Config::ConnectWithoutContext("/NodeList/*/DeviceList/*/LteEnbRrc/RrcTimeout",
                                  MakeCallback(&EnbRrcTimeout));

    NS_LOG_INFO("Starting simulation...");
    Simulator::Stop(simTime);
    Simulator::Run();
    Simulator::Destroy();

    return 0;
}