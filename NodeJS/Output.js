'use strict';

/* 

	Description:  

		This class can output JSON, XML, OBJECT.

	NPM Doc: 

		https://www.npmjs.com/package/pixl-xml#preserve-sort-order

*/

const XML = require('pixl-xml');

const classname = 'Network::Output';

exports.Output = class { 

	/*
		input                :  Object or string allowed.
		output_type (string) :  json, xml, obj.
		is_json (int)        :  required if parsing json input.
		reply_tag (string)   :  Example 'LocationsReply'
		namespace (string)   :  Example 'Locations'
	*/
	async init( args ) {

		args = args || [];

		let input       = args['input']; 
		let is_json     = args['is_json'];
		let reply_tag   = args['reply_tag'] || 'DefaultReply';
		let namespace   = args['namespace'];
		let output_type = args['output_type'];

		// Can be obj, string.
		let result = '';

		if ( input ) {

			// Determine the input type.
			let type_of = typeof input;

			// Convert XML (string) into an obj.
			if ( type_of == 'string' ) {

				let doc     = {};
				output_type = 'object';

				try { 

					// Convert xml, json into an obj.
					if ( is_json ) {
						doc = JSON.parse( input, { preserveAttributes: true, preserveWhitespace: true } );
					} else {
						doc = XML.parse( input );
					}

				} catch( e ) {
					// Trace here.
				}

				if ( typeof doc === 'object' ) {
					result = doc;
				}

			} else if ( type_of == 'object' ) {

				// Convert obj into an json or xml.
				output_type = output_type ? output_type : 'xml';

			}

			// Output.
			if ( !result ) {

				if ( output_type == 'xml' ) {

					// Build the xml reply and replace the top tag with namespace.
					result = XML.stringify( input, reply_tag, 0, "\t", "\n", false );

					if ( namespace ) {
						let ns_string = 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://example.com/xxx/' + namespace + '"';
						let reply_tag_top = `${reply_tag} ${ns_string}`;
						result            = result.replace( reply_tag, reply_tag_top );
					} else { 
						result = result.replace( /<\?xml version="1.0"\?>\n/, '' );
					}

				} else if ( output_type == 'json' ) { 
					result = JSON.stringify( input );
				}

			}
		}

		return result;
	}
}
