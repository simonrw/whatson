module Main exposing (..)

import Array
import Browser
import Html exposing (Html, a, div, h1, img, option, p, select, text)
import Html.Attributes exposing (class, href, src, value)
import Html.Events exposing (onInput)
import Http
import Json.Decode as D
import Json.Encode as E


type alias RawDate =
    { year : Int
    , month : Int
    , day : Int
    }


rawDateToString : RawDate -> String
rawDateToString r =
    String.fromInt r.day ++ "-" ++ String.fromInt r.month ++ "-" ++ String.fromInt r.year


type alias Show =
    { name : String
    , theatre : String
    , imageUrl : String
    , linkUrl : String
    , startDate : RawDate
    , endDate : RawDate
    }


type alias Shows =
    List Show


type alias Model =
    { availableMonths : List DateElement
    , selectedMonth : Maybe DateElement
    , shows : List Show
    }


initModel : Model
initModel =
    { availableMonths = []
    , selectedMonth = Nothing
    , shows = []
    }


type alias DateElement =
    { month : Int
    , year : Int
    }


init : () -> ( Model, Cmd Msg )
init _ =
    ( initModel
    , Http.get
        { url = "/api/months"
        , expect = Http.expectJson GotMonths monthsDecoder
        }
    )


monthsDecoder : D.Decoder (List DateElement)
monthsDecoder =
    D.field "dates" (D.list decodeDateElement)


decodeDateElement : D.Decoder DateElement
decodeDateElement =
    D.map2 DateElement
        (D.field "month" D.int)
        (D.field "year" D.int)


type Msg
    = GotMonths (Result Http.Error (List DateElement))
    | GotShows (Result Http.Error Shows)
    | SelectedMonth String


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        GotMonths response ->
            case response of
                Ok months ->
                    ( { model | availableMonths = months }, Cmd.none )

                Err e ->
                    let
                        _ =
                            Debug.log "error" e
                    in
                    ( model, Cmd.none )

        GotShows response ->
            case response of
                Ok shows ->
                    ( { model | shows = shows }, Cmd.none )

                Err e ->
                    let
                        _ =
                            Debug.log "error" e
                    in
                    ( model, Cmd.none )

        SelectedMonth selectedMonth ->
            String.toInt selectedMonth
                |> Maybe.map
                    (\i ->
                        let
                            selected =
                                model.availableMonths
                                    |> Array.fromList
                                    |> Array.get i

                            newModel =
                                { model | selectedMonth = selected }
                        in
                        ( newModel, fetchShows newModel )
                    )
                |> Maybe.withDefault ( model, Cmd.none )


bodyFromModel : Model -> E.Value
bodyFromModel model =
    model.selectedMonth
        |> Maybe.map
            (\m ->
                E.object
                    [ ( "year", E.int m.year )
                    , ( "month", E.int m.month )
                    ]
            )
        |> Maybe.withDefault E.null


fetchShows : Model -> Cmd Msg
fetchShows model =
    Http.post
        { url = "/api/shows"
        , expect = Http.expectJson GotShows showsDecoder
        , body = Http.jsonBody <| bodyFromModel model
        }


showsDecoder : D.Decoder Shows
showsDecoder =
    D.field "shows" <| D.list showDecoder


showDecoder : D.Decoder Show
showDecoder =
    D.map6 Show
        (D.field "name" D.string)
        (D.field "theatre" D.string)
        (D.field "image_url" D.string)
        (D.field "link_url" D.string)
        (D.field "start_date" rawDateDecoder)
        (D.field "end_date" rawDateDecoder)


rawDateDecoder : D.Decoder RawDate
rawDateDecoder =
    D.string
        |> D.andThen
            (\s ->
                let
                    parts =
                        s
                            |> String.split "-"
                            |> List.map String.toInt
                            |> List.map (Maybe.withDefault -1)

                    date =
                        case parts of
                            [ year, month, day ] ->
                                RawDate year month day

                            _ ->
                                RawDate 0 0 0
                in
                D.succeed date
            )


view : Model -> Html Msg
view model =
    div [ class "text-gray-900 p-16" ]
        [ h1 [ class "text-3xl font-semibold" ]
            [ text "What's on?"
            ]
        , modelSelect model
        , viewShows model.shows
        ]


viewShows : Shows -> Html Msg
viewShows shows =
    div [ class "flex flex-wrap" ] <|
        List.map viewShow shows


viewShow : Show -> Html Msg
viewShow show =
    div [ class "shadow w-64 m-8 p-8" ]
        [ a [ href show.linkUrl ]
            [ img [ class "w-64", src show.imageUrl ] []
            , p [ class "text-lg font-semibold" ]
                [ text show.name ]
            , p []
                [ text show.theatre ]
            , p []
                [ text <| rawDateToString show.startDate ++ " to " ++ rawDateToString show.endDate ]
            ]
        ]


monthIntToString m =
    case m of
        1 ->
            "January"

        2 ->
            "February"

        3 ->
            "March"

        4 ->
            "April"

        5 ->
            "May"

        6 ->
            "June"

        7 ->
            "July"

        8 ->
            "August"

        9 ->
            "September"

        10 ->
            "October"

        11 ->
            "November"

        12 ->
            "December"

        _ ->
            "Unknown"


modelSelect : Model -> Html Msg
modelSelect model =
    if List.length model.availableMonths == 0 then
        div [] []

    else
        let
            optionFromMonth i m =
                option [ value <| String.fromInt i ] [ text <| monthIntToString m.month ++ " " ++ String.fromInt m.year ]

            initialValue =
                option [ value "" ] [ text "-" ]
        in
        select [ class "block appearance-none bg-white border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline", onInput (\i -> SelectedMonth i) ] <|
            [ initialValue
            ]
                ++ List.indexedMap optionFromMonth model.availableMonths


main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions =
            \_ ->
                Sub.none
        }
