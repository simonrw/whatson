module Main exposing (..)

import Array
import Browser
import Html exposing (Html, a, div, h1, img, label, option, p, select, span, text)
import Html.Attributes exposing (class, for, href, id, src, value)
import Html.Events exposing (onInput)
import Http
import Json.Decode as D
import Json.Encode as E
import Set exposing (Set)


type alias RawDate =
    { year : Int
    , month : Int
    , day : Int
    }


rawDateToString : RawDate -> String
rawDateToString r =
    let
        monthStr =
            Array.fromList [ "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]
                |> Array.get (r.month - 1)
                |> Maybe.withDefault "??"

        dayStr =
            Array.fromList [ "1st", "2nd", "3rd" ]
                |> Array.get r.day
                |> Maybe.withDefault (String.fromInt r.day ++ "th")
    in
    dayStr ++ " " ++ monthStr ++ " " ++ String.fromInt r.year


compareDates : RawDate -> RawDate -> Order
compareDates a b =
    case compare a.year b.year of
        LT ->
            LT

        GT ->
            GT

        EQ ->
            case compare a.month b.month of
                LT ->
                    LT

                GT ->
                    GT

                EQ ->
                    compare a.day b.day


type alias Show =
    { name : String
    , theatre : String
    , imageUrl : String
    , linkUrl : String
    , startDate : RawDate
    , endDate : RawDate
    }


compareShowsByDate : Show -> Show -> Order
compareShowsByDate a b =
    compareDates a.startDate b.startDate


type alias Shows =
    List Show


type SortSelection
    = Date
    | Name


type alias Model =
    { availableMonths : List DateElement
    , selectedMonth : Maybe DateElement
    , shows : List Show
    , sortSelection : SortSelection
    , theatres : Set String
    , filterTheatre : Maybe String
    , error : Maybe String
    }


initModel : Model
initModel =
    { availableMonths = []
    , selectedMonth = Nothing
    , shows = []
    , sortSelection = Date
    , theatres = Set.empty
    , filterTheatre = Nothing
    , error = Nothing
    }


type alias DateElement =
    { month : Int
    , year : Int
    }


compareDateElements : DateElement -> DateElement -> Order
compareDateElements a b =
    case compare a.year b.year of
        LT ->
            LT

        GT ->
            GT

        EQ ->
            compare a.month b.month


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
    | SelectedSort SortSelection
    | SelectedTheatre (Maybe String)


httpErrorToString : Http.Error -> String
httpErrorToString e =
  case e of
    Http.BadUrl s ->
      "Bad URL: " ++ s

    Http.Timeout ->
      "Request timed out"

    Http.NetworkError ->
      "A network error occurred"

    Http.BadStatus s ->
      "A bad status code was received: " ++ String.fromInt s

    Http.BadBody s ->
      "A bad body was received: " ++ s


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        GotMonths response ->
            case response of
                Ok months ->
                    ( { model | availableMonths = List.sortWith compareDateElements months }, Cmd.none )

                Err e ->
                    ( { model | error = Just <| httpErrorToString e }, Cmd.none )

        GotShows response ->
            case response of
                Ok shows ->
                    let
                        theatres =
                            List.map .theatre shows
                                |> Set.fromList
                    in
                    ( { model | shows = shows, theatres = theatres }, Cmd.none )

                Err e ->
                    ( { model | error = Just <| httpErrorToString e }, Cmd.none )

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

        SelectedSort selectedSort ->
            ( { model | sortSelection = selectedSort }, Cmd.none )

        SelectedTheatre selectedTheatre ->
            ( { model | filterTheatre = selectedTheatre }, Cmd.none )


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
  case model.error of
    Nothing ->
      div [ class "text-white p-4 m-4 flex-col md:text-2xl lg:text-lg" ]
          [ div [ class "flex-shrink-0" ]
              [ h1 [ class "text-3xl md:text-5xl font-semibold mb-8" ]
                  [ text "What's on?"
                  ]
              , modelSelect model
              ]
          , div []
              [ viewShows model
              ]
          ]

    Just e ->
      div [ class "text-white p-4 m-4 flex-col md:text-2xl lg:text-lg" ]
        [ div [ class "flex-shrink-0" ]
          [ h1 [ class "text-3xl md:text-5xl font-semibold mb-8" ]
            [ text "Error" ]
          , p []
            [ text e ]
          ]
        ]


viewShows : Model -> Html Msg
viewShows { sortSelection, shows, filterTheatre } =
    let
        sortedShows =
            case sortSelection of
                Name ->
                    List.sortBy .name shows

                Date ->
                    List.sortWith compareShowsByDate shows

        toShowShows =
            case filterTheatre of
                Just t ->
                    List.filter (\s -> s.theatre == t) sortedShows

                Nothing ->
                    sortedShows
    in
    div [ class "flex flex-wrap md:justify-around" ] <|
        List.map viewShow toShowShows


viewShow : Show -> Html Msg
viewShow show =
    let
        -- We want to prevent line breaks in dates, so we must handle the case
        -- when the dates are equal, in which case we only show the one date.
        -- If the dates are different, then show the two dates with " to "
        -- inbetween them.
        dateElem =
            if show.startDate == show.endDate then
                [ span [ class "whitespace-no-wrap" ] [ text <| rawDateToString show.startDate ] ]

            else
                [ span [ class "whitespace-no-wrap" ] [ text <| rawDateToString show.startDate ]
                , text " to "
                , span [ class "whitespace-no-wrap" ] [ text <| rawDateToString show.endDate ]
                ]
    in
    div [ class "md:flex-grow lg:flex-grow-0 shadow bg-gray-100 flex text-gray-900 rounded-lg md:w-64 p-4 mb-4 md:m-4" ]
        [ a [ href show.linkUrl, class "flex flex-col flex-grow justify-between" ]
            [ div [ class "flex flex-col" ]
                [ img [ class "w-screen md:w-64 mb-8", src show.imageUrl ] []
                , p [ class "text-2xl tracking-tight font-semibold mb-4" ]
                    [ text show.name ]
                , p [ class "mb-4" ]
                    [ text <| "@ " ++ show.theatre ]
                ]
            , p []
                dateElem
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

            optionFromTheatre t =
                option [ value t ] [ text t ]
        in
        div [ class "mb-8" ]
            [ div [ class "my-4" ]
                [ label [ for "select-time" ] [ text "Choose a month" ]
                , select [ id "select-time", class "block appearance-none bg-white text-gray-900 border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline", onInput (\i -> SelectedMonth i) ] <|
                    [ initialValue
                    ]
                        ++ List.indexedMap optionFromMonth model.availableMonths
                ]
            , div [ class "my-4" ]
                [ label [ for "select-sort" ] [ text "Sort by" ]
                , select
                    [ id "select-sort"
                    , class "block appearance-none bg-white text-gray-900 border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline"
                    , onInput
                        (\s ->
                            case s of
                                "sort-by-name" ->
                                    SelectedSort Name

                                "sort-by-date" ->
                                    SelectedSort Date

                                _ ->
                                    SelectedSort Date
                        )
                    ]
                    [ option [ value "sort-by-date" ] [ text "Date" ]
                    , option [ value "sort-by-name" ] [ text "Name" ]
                    ]
                ]
            , div [ class "my-4" ]
                [ label [ for "select-theatre" ] [ text "Single theatre" ]
                , select
                    [ id "select-theatre"
                    , class "block appearance-none bg-white border text-gray-900 border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline"
                    , onInput
                        (\s ->
                            case s of
                                "" ->
                                    SelectedTheatre Nothing

                                t ->
                                    SelectedTheatre (Just t)
                        )
                    ]
                    ([ initialValue
                     ]
                        ++ List.map optionFromTheatre (Set.toList model.theatres)
                    )
                ]
            ]


main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions =
            \_ ->
                Sub.none
        }
